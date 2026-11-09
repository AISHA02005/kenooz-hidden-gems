export const CATEGORIES = [
  "Historical Places",
  "Beaches & Nature",
  "Cafés & Restaurants",
  "Photography Spots",
  "Other",
] as const;

export type Category = (typeof CATEGORIES)[number];

export const GOVERNORATES = [
  "Alexandria",
  "Aswan",
  "Beheira",
  "Beni Suef",
  "Cairo",
  "Dakahlia",
  "Damietta",
  "Faiyum",
  "Gharbia",
  "Giza",
  "Ismailia",
  "Kafr El Sheikh",
  "Luxor",
  "Matrouh",
  "Minya",
  "Monufia",
  "New Valley",
  "North Sinai",
  "Port Said",
  "Qalyubia",
  "Qena",
  "Red Sea",
  "Sharqia",
  "Sohag",
  "South Sinai",
  "Suez",
  "Asyut",
].sort();

export type Place = {
  id: string;
  name: string;
  category: Category;
  governorate: string;
  description: string;
  image: string;
};

export const PLACES: Place[] = [
  {
    id: "shali-fortress",
    name: "Shali Fortress",
    category: "Historical Places",
    governorate: "Matrouh",
    description:
      "A 13th-century mudbrick citadel rising above the palm groves of Siwa Oasis, best visited at sunset.",
    image: "/places/siwa-shali.png",
  },
  {
    id: "blue-hole",
    name: "Blue Hole Coast",
    category: "Beaches & Nature",
    governorate: "South Sinai",
    description:
      "Red mountains meet crystal reef waters north of Dahab, a calm spot for snorkeling away from the crowds.",
    image: "/places/blue-hole-dahab.png",
  },
  {
    id: "el-fishawy",
    name: "El Fishawy Café",
    category: "Cafés & Restaurants",
    governorate: "Cairo",
    description:
      "A centuries-old café tucked inside Khan el-Khalili, known for its mirrors, lanterns, and mint tea.",
    image: "/places/el-fishawy.png",
  },
  {
    id: "white-desert",
    name: "White Desert",
    category: "Photography Spots",
    governorate: "New Valley",
    description:
      "Wind-carved chalk formations near Farafra that glow orange at dusk and silver under the stars.",
    image: "/places/white-desert.png",
  },
  {
    id: "tuna-el-gebel",
    name: "Tuna el-Gebel",
    category: "Historical Places",
    governorate: "Minya",
    description:
      "An ancient necropolis with the beautifully carved tomb of Petosiris, blending Egyptian and Greek art.",
    image: "/places/tuna-el-gebel.png",
  },
  {
    id: "gharb-soheil",
    name: "Gharb Soheil Village",
    category: "Other",
    governorate: "Aswan",
    description:
      "A colorful Nubian village on the Nile's west bank with painted homes, local crafts, and warm hospitality.",
    image: "/places/gharb-soheil.png",
  },
];
