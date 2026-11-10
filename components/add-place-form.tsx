"use client";

import { useEffect, useState } from "react";
import { buttonStyles, fieldStyles } from "@/components/ui";
import { CATEGORIES, GOVERNORATES, type Place } from "@/lib/places";

type FieldName = "name" | "category" | "governorate" | "image" | "description";
type Errors = Partial<Record<FieldName, string>> & { general?: string };

const MAX_IMAGE_MB = 5;
const ALLOWED_MIME_TYPES = ["image/jpeg", "image/png", "image/jpg"];

function validate(form: FormData): Errors {
  const errors: Errors = {};
  const name = String(form.get("name") ?? "").trim();
  const description = String(form.get("description") ?? "").trim();
  const image = form.get("image");

  if (!name) {
    errors.name = "Please enter the place name.";
  } else if (name.length < 3) {
    errors.name = "Place name must be at least 3 characters.";
  } else if (name.length > 100) {
    errors.name = "Place name must not exceed 100 characters.";
  }

  if (!form.get("category")) {
    errors.category = "Please choose a category.";
  }

  if (!form.get("governorate")) {
    errors.governorate = "Please choose a governorate.";
  }

  if (description.length > 500) {
    errors.description = "Description must not exceed 500 characters.";
  }

  if (!(image instanceof File) || image.size === 0) {
    errors.image = "Please upload an image of the place.";
  } else if (!ALLOWED_MIME_TYPES.includes(image.type.toLowerCase())) {
    errors.image = "The file must be an image (JPG or PNG only).";
  } else if (image.size > MAX_IMAGE_MB * 1024 * 1024) {
    errors.image = `Image must be smaller than ${MAX_IMAGE_MB} MB.`;
  }

  return errors;
}

function FieldError({ id, message }: { id: string; message?: string }) {
  if (!message) return null;
  return (
    <p id={id} className="text-sm font-medium text-primary-strong">
      {message}
    </p>
  );
}

export function AddPlaceForm() {
  const [errors, setErrors] = useState<Errors>({});
  const [submittedPlace, setSubmittedPlace] = useState<Place | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    return () => {
      if (preview) URL.revokeObjectURL(preview);
    };
  }, [preview]);

  function handleImageChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file && ALLOWED_MIME_TYPES.includes(file.type.toLowerCase())) {
      setPreview(URL.createObjectURL(file));
    } else {
      setPreview(null);
    }
    setErrors((prev) => ({ ...prev, image: undefined, general: undefined }));
  }

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const formEl = e.currentTarget;
    const data = new FormData(formEl);

    // Client-side pre-validation
    const clientErrors = validate(data);
    if (Object.keys(clientErrors).length > 0) {
      setErrors(clientErrors);
      const firstInvalid = Object.keys(clientErrors)[0];
      if (firstInvalid) {
        formEl.querySelector<HTMLElement>(`[name="${firstInvalid}"]`)?.focus();
      }
      return;
    }

    setIsSubmitting(true);
    setErrors({});

    try {
      // POST to /api/places without manual Content-Type header so browser sets multipart boundary
      const res = await fetch("/api/places", {
        method: "POST",
        body: data,
        headers: {
          Accept: "application/json",
        },
      });

      const responseData = await res.json();

      if (!res.ok) {
        if (res.status === 400 && responseData.details) {
          setErrors(responseData.details);
          const firstInvalid = Object.keys(responseData.details)[0];
          if (firstInvalid) {
            formEl.querySelector<HTMLElement>(`[name="${firstInvalid}"]`)?.focus();
          }
        } else {
          setErrors({
            general: responseData.error || responseData.message || "Failed to submit place. Please try again.",
          });
        }
        return;
      }

      // Success: place is created with status 'pending'
      setSubmittedPlace(responseData.place);
      formEl.reset();
      setPreview(null);
    } catch {
      setErrors({
        general: "Unable to reach the server. Please verify that the Flask backend is running on http://127.0.0.1:5000.",
      });
    } finally {
      setIsSubmitting(false);
    }
  }

  function clearError(field: FieldName) {
    if (errors[field] || errors.general) {
      setErrors((prev) => ({ ...prev, [field]: undefined, general: undefined }));
    }
  }

  if (submittedPlace) {
    return (
      <div
        role="status"
        className="rounded-lg border border-border bg-card p-8 text-center shadow-sm shadow-primary/5 md:p-12"
      >
        <div
          aria-hidden="true"
          className="sunset-gradient mx-auto flex h-14 w-14 items-center justify-center rounded-full text-2xl font-bold text-primary-foreground"
        >
          {"\u2713"}
        </div>
        <h2 className="mt-6 font-serif text-3xl font-semibold">Thank you for sharing!</h2>
        <p className="mx-auto mt-3 max-w-md leading-relaxed text-muted">
          <span className="font-semibold text-foreground">{submittedPlace.name}</span> has been submitted
          for review. It is currently <span className="font-semibold text-primary-strong">pending approval</span> and
          will appear on the Explore page once approved by our moderation team.
        </p>
        <button
          type="button"
          onClick={() => setSubmittedPlace(null)}
          className={`${buttonStyles.primary} mt-8`}
        >
          Add another place
        </button>
      </div>
    );
  }

  return (
    <form
      noValidate
      onSubmit={handleSubmit}
      className="flex flex-col gap-6 rounded-lg border border-border bg-card p-6 shadow-sm shadow-primary/5 md:p-8"
    >
      {errors.general && (
        <div
          role="alert"
          className="rounded-md border border-primary-strong/40 bg-primary/10 p-4 text-sm text-primary-strong"
        >
          {errors.general}
        </div>
      )}

      <div className="flex flex-col gap-1.5">
        <label htmlFor="name" className="text-sm font-medium">
          Place name <span className="text-primary-strong">*</span>
        </label>
        <input
          id="name"
          name="name"
          type="text"
          required
          maxLength={100}
          placeholder="e.g. Wadi El Hitan"
          aria-invalid={Boolean(errors.name)}
          aria-describedby={errors.name ? "name-error" : undefined}
          onChange={() => clearError("name")}
          disabled={isSubmitting}
          className={fieldStyles}
        />
        <FieldError id="name-error" message={errors.name} />
      </div>

      <div className="grid gap-6 sm:grid-cols-2">
        <div className="flex flex-col gap-1.5">
          <label htmlFor="category" className="text-sm font-medium">
            Category <span className="text-primary-strong">*</span>
          </label>
          <select
            id="category"
            name="category"
            required
            defaultValue=""
            aria-invalid={Boolean(errors.category)}
            aria-describedby={errors.category ? "category-error" : undefined}
            onChange={() => clearError("category")}
            disabled={isSubmitting}
            className={fieldStyles}
          >
            <option value="" disabled>
              Select a category
            </option>
            {CATEGORIES.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
          <FieldError id="category-error" message={errors.category} />
        </div>

        <div className="flex flex-col gap-1.5">
          <label htmlFor="governorate" className="text-sm font-medium">
            Governorate <span className="text-primary-strong">*</span>
          </label>
          <select
            id="governorate"
            name="governorate"
            required
            defaultValue=""
            aria-invalid={Boolean(errors.governorate)}
            aria-describedby={errors.governorate ? "governorate-error" : undefined}
            onChange={() => clearError("governorate")}
            disabled={isSubmitting}
            className={fieldStyles}
          >
            <option value="" disabled>
              Select a governorate
            </option>
            {GOVERNORATES.map((g) => (
              <option key={g} value={g}>
                {g}
              </option>
            ))}
          </select>
          <FieldError id="governorate-error" message={errors.governorate} />
        </div>
      </div>

      <div className="flex flex-col gap-1.5">
        <label htmlFor="description" className="text-sm font-medium">
          Description <span className="font-normal text-muted">(optional)</span>
        </label>
        <textarea
          id="description"
          name="description"
          rows={4}
          maxLength={500}
          placeholder="What makes this place special? Any tips for visitors?"
          onChange={() => clearError("description")}
          disabled={isSubmitting}
          className={`${fieldStyles} resize-y`}
        />
        <FieldError id="description-error" message={errors.description} />
      </div>

      <div className="flex flex-col gap-1.5">
        <label htmlFor="image" className="text-sm font-medium">
          Place image <span className="text-primary-strong">*</span>
        </label>
        <input
          id="image"
          name="image"
          type="file"
          accept="image/jpeg,image/png"
          required
          aria-invalid={Boolean(errors.image)}
          aria-describedby={errors.image ? "image-error image-hint" : "image-hint"}
          onChange={handleImageChange}
          disabled={isSubmitting}
          className={`${fieldStyles} cursor-pointer file:mr-4 file:cursor-pointer file:rounded-md file:border-0 file:bg-primary/10 file:px-4 file:py-1.5 file:text-sm file:font-semibold file:text-primary-strong hover:file:bg-primary/15`}
        />
        <p id="image-hint" className="text-xs text-muted">
          JPG or PNG up to {MAX_IMAGE_MB} MB.
        </p>
        <FieldError id="image-error" message={errors.image} />
        {preview && (
          // eslint-disable-next-line @next/next/no-img-element -- local blob preview, not optimizable
          <img
            src={preview}
            alt="Selected place preview"
            className="mt-2 aspect-[4/3] w-full max-w-xs rounded-md border border-border object-cover"
          />
        )}
      </div>

      <div className="flex flex-col-reverse gap-3 border-t border-border pt-6 sm:flex-row sm:items-center sm:justify-between">
        <p className="text-xs text-muted">
          <span className="text-primary-strong">*</span> Required fields
        </p>
        <button
          type="submit"
          disabled={isSubmitting}
          className={`${buttonStyles.primary} disabled:cursor-not-allowed disabled:opacity-60`}
        >
          {isSubmitting ? "Submitting place..." : "Submit place"}
        </button>
      </div>
    </form>
  );
}
