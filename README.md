# Maria Bonete's portfolio

The source of [mariabonete.netlify.app](https://mariabonete.netlify.app): my work as a full-stack developer, web and mobile (React Native and native Android), with case studies for Marine Wobbles, Quote & Nod and Doorplate.

## Stack

Next.js 16 (App Router), React 19, TypeScript and Tailwind CSS 4, deployed on Netlify. No other runtime libraries.

## How it's put together

- **The hero** is a studio rendered in Blender, with every object modelled in Python in `tools/studio/`. The conga, the maracas and the keyboard answer a click with a recording: each is rendered as a layer of its own from the same camera, so it can move over the room while its shadow stays on the floor. With reduced motion on, they play their sound and stay still. Textures and sounds are CC0, listed in `tools/studio/ASSETS.md`.
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

Rendering the hero again needs Blender, ImageMagick, `cwebp` and ffmpeg. The steps are in `tools/studio/README.md`; the folding screen in the studio is painted from the panels in `tools/gold-screen/`.
