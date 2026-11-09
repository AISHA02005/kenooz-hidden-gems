"use client";

import { useEffect, useState } from "react";
import { buttonStyles, fieldStyles } from "@/components/ui";
import { CATEGORIES, GOVERNORATES } from "@/lib/places";

type FieldName = "name" | "category" | "governorate" | "image";
type Errors = Partial<Record<FieldName, string>>;

const MAX_IMAGE_MB = 5;

function validate(form: FormData): Errors {
  const errors: Errors = {};
  const name = String(form.get("name") ?? "").trim();
  const image = form.get("image");

  if (!name) errors.name = "Please enter the place name.";
  else if (name.length < 3) errors.name = "Place name must be at least 3 characters.";
  if (!form.get("category")) errors.category = "Please choose a category.";
  if (!form.get("governorate")) errors.governorate = "Please choose a governorate.";

  if (!(image instanceof File) || image.size === 0) {
    errors.image = "Please upload an image of the place.";
  } else if (!image.type.startsWith("image/")) {
    errors.image = "The file must be an image (JPG, PNG, or WebP).";
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
  const [submittedName, setSubmittedName] = useState<string | null>(null);
  const [preview, setPreview] = useState<string | null>(null);

  useEffect(() => {
    return () => {
      if (preview) URL.revokeObjectURL(preview);
    };
  }, [preview]);

  function handleImageChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    setPreview(file && file.type.startsWith("image/") ? URL.createObjectURL(file) : null);
    setErrors((prev) => ({ ...prev, image: undefined }));
  }

  function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const formEl = e.currentTarget;
    const data = new FormData(formEl);
    const nextErrors = validate(data);
    setErrors(nextErrors);

    const firstInvalid = Object.keys(nextErrors)[0];
    if (firstInvalid) {
      formEl.querySelector<HTMLElement>(`[name="${firstInvalid}"]`)?.focus();
      return;
    }

    setSubmittedName(String(data.get("name")).trim());
    formEl.reset();
    setPreview(null);
  }

  function clearError(field: FieldName) {
    if (errors[field]) setErrors((prev) => ({ ...prev, [field]: undefined }));
  }

  if (submittedName) {
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
          <span className="font-semibold text-foreground">{submittedName}</span> has been submitted
          for review. Once approved, it will appear on the Explore page for other travelers.
        </p>
        <button
          type="button"
          onClick={() => setSubmittedName(null)}
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
          className={`${fieldStyles} resize-y`}
        />
      </div>

      <div className="flex flex-col gap-1.5">
        <label htmlFor="image" className="text-sm font-medium">
          Place image <span className="text-primary-strong">*</span>
        </label>
        <input
          id="image"
          name="image"
          type="file"
          accept="image/*"
          required
          aria-invalid={Boolean(errors.image)}
          aria-describedby={errors.image ? "image-error image-hint" : "image-hint"}
          onChange={handleImageChange}
          className={`${fieldStyles} cursor-pointer file:mr-4 file:cursor-pointer file:rounded-md file:border-0 file:bg-primary/10 file:px-4 file:py-1.5 file:text-sm file:font-semibold file:text-primary-strong hover:file:bg-primary/15`}
        />
        <p id="image-hint" className="text-xs text-muted">
          JPG, PNG, or WebP up to {MAX_IMAGE_MB} MB.
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
        <button type="submit" className={buttonStyles.primary}>
          Submit place
        </button>
      </div>
    </form>
  );
}
