import type { Metadata } from "next";

// Where the site is published: link previews need full addresses for their page and image. Switch to
// https://mariabonete.com once quill serves it over HTTPS.
export const siteUrl = new URL("https://mariabonete.netlify.app");

// The images in public/og (1200x630), made from the site itself, and what each one shows.
const images = {
  site: "Maria Bonete, full-stack developer: her name above a studio on a blue ground, with a gold folding screen, a desk with three monitors, a plush capybara, a conga and an easel.",
  "quote-and-nod": "Quote & Nod's job page with two vendor quotes, in a browser window and on a phone.",
  doorplate: "A Doorplate listing in a browser window, and the form to write to its owner on a phone.",
  "marine-wobbles": "Marine Wobbles on three phones: level 2, the Sakura Waters map and level 66.",
  switchboard: "Switchboard's web dashboard in a browser window, with its cmux panel standing in front, on a saffron ground.",
};

// The card a page gets when its link is shared on LinkedIn, Slack, WhatsApp and the like: its title,
// description, address and image. X reads the same tags.
export function share(page: {
  title: string;
  description: string;
  path: string;
  image: keyof typeof images;
}): Pick<Metadata, "openGraph"> {
  return {
    openGraph: {
      type: "website",
      siteName: "Maria Bonete",
      title: page.title,
      description: page.description,
      url: page.path,
      images: [{ url: `/og/${page.image}.jpg`, width: 1200, height: 630, alt: images[page.image] }],
    },
  };
}
