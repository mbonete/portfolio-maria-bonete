# Maria Bonete's portfolio

The source of [mariabonete.netlify.app](https://mariabonete.netlify.app): my work as a full-stack developer, web and mobile (React Native and native Android), with case studies for Marine Wobbles, Quote & Nod and Doorplate.

## Stack

Next.js 16 (App Router), React 19, TypeScript and Tailwind CSS 4, deployed on Netlify. No other runtime libraries.

## How it's put together

- **The hero** is a four-panel folding screen rendered in Blender: 28 frames from nearly shut to open, each split into a back and a front plate, so my name sits behind the panels that fold toward you and in front of the others. The page plays the frames on two canvases with a cross-fade between them, and shows the open screen as a still when reduced motion is on. The Blender scene and the scripts that paint, render and encode it are in `tools/gold-screen/`.
- **Each project** gets one flat colour and its real product, in a browser window, on a phone or both. The phones play short silent loops of the product in use.
- **Demo videos** play from YouTube's privacy-enhanced domain, and nothing from YouTube loads until you press play.
- **Most of the copy** lives in `src/content.ts`, and all of it follows the writing rules in `CLAUDE.md`. `PRODUCT.md` describes the audience and the constraints, and `docs/` records design decisions.

How I built it with coding agents is on the site: [How this site was built](https://mariabonete.netlify.app/how-this-site-was-built).

## Running it

```bash
npm install
npm run dev     # http://localhost:3000
npm run build   # production build
```

Rendering the hero again needs Blender, ImageMagick and `cwebp`. Each script in `tools/gold-screen/` opens with a comment on what it does and in which order to run it.
