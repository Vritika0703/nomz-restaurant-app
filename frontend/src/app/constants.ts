/** Cuisine choices matching Restaurant.CUISINE_CHOICES from the backend. */
export const CUISINE_CHOICES: { value: string; label: string }[] = [
  { value: "american", label: "American" },
  { value: "asian", label: "Asian" },
  { value: "italian", label: "Italian" },
  { value: "mexican", label: "Mexican" },
  { value: "indian", label: "Indian" },
  { value: "french", label: "French" },
  { value: "japanese", label: "Japanese" },
  { value: "chinese", label: "Chinese" },
  { value: "thai", label: "Thai" },
  { value: "mediterranean", label: "Mediterranean" },
  { value: "fusion", label: "Fusion" },
  { value: "vegetarian", label: "Vegetarian" },
  { value: "vegan", label: "Vegan" },
  { value: "other", label: "Other" },
];

/** Price choices matching Restaurant.PRICE_CHOICES from the backend. */
export const PRICE_CHOICES: { value: string; label: string }[] = [
  { value: "$", label: "Budget-Friendly ($)" },
  { value: "$$", label: "Moderate ($$)" },
  { value: "$$$", label: "Upscale ($$$)" },
  { value: "$$$$", label: "Fine Dining ($$$$)" },
];