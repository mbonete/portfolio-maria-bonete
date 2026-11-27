# Maria Bonete's portfolio

The source of [mariabonete.netlify.app](https://mariabonete.netlify.app): my work as a full-stack developer, web and mobile (React Native and native Android), with case studies for Marine Wobbles, Quote & Nod and Doorplate.

## Stack

Next.js 16 (App Router), React 19, TypeScript and Tailwind CSS 4, deployed on Netlify. No other runtime libraries.

## How it's put together

- **The hero** is a studio rendered in Blender, with every object modelled in Python in `tools/studio/`. Nine things in it answer a click, eight of them with a recording. Each of those eight is rendered as a layer of its own from the same camera: the ones that move as cut-outs over the room, whose shadows stay on the floor; the lights as light added on top; the painting's stages and the computer's colours shown in place. Clicking the monitors scrolls the code on the middle one, a tall image of the file placed on the screen with a CSS `matrix3d` computed from the Blender camera. For five seconds after the room appears, the computer's lights go through their colours, the keyboard's LEDs flare and the code scrolls, with no click and no sound. With reduced motion on, nothing moves and none of that plays by itself, but the sounds play, the lights and the painting still change, and a click on the monitors shows the next lines of code at once. Textures and sounds are CC0, listed in `tools/studio/ASSETS.md`.
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
