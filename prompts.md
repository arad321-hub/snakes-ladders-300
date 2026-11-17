# פרומפטים לרקעים הריאליסטיים

5 תמונות, אחת לכל עולם. כל פרומפט עומד בפני עצמו, אז אפשר להעתיק אותו כמו שהוא לכל כלי.

## הנחיות כלליות

- **יחס תמונה:** הכי רחב שהכלי מאפשר. רצועת עולם על הלוח היא ביחס 20:3 (רחבה מאוד). אם אפשר לבחור, בחר 3:1, ואם לא, 21:9. אני חותך מהתמונה רצועה ביחס 20:3, וגם עוד קצת גובה בשביל המעבר בין העולמות. התמונה לא נמתחת ולא מעוותת, רק נחתכת. לכן הפרומפטים מבקשים לשים את כל התוכן החשוב בפס האמצעי. ב-Midjourney אפשר לנסות גם `--ar 20:3`.
  - Midjourney: הוסף `--ar 3:1` בסוף הפרומפט.
  - ChatGPT / Gemini / Firefly: בחר את הפורמט הרוחבי הרחב ביותר.
- **רזולוציה:** אחרי היצירה, הגדל פי 4 (Upscayl החינמי, Topaz, Magnific). היעד הוא לפחות 3,500 פיקסלים ברוחב, ועדיף 7,000.
- **עקביות:** צור את כל ה-5 באותו כלי ובאותה שיחה או סשן. אם תמונה אחת יוצאת חריגה בסגנון או בבהירות, צור אותה מחדש.
- **שמות קבצים להעלאה:** `meadow.png`, `desert.png`, `jungle.png`, `arctic.png`, `space.png`.
- **עמעום:** הפרומפטים כבר מבקשים רקע מעומעם ונסוג. בנוסף, בקוד יש בקרת עמעום שאפשר לכוונן אחרי שהתמונות מגיעות.

---

## 1. אחו (שורות 1–3, משבצות 1–60)

```
Create an image: a wide panoramic realistic landscape of a gentle green meadow with soft rolling hills, scattered small wildflowers in white, yellow and pink, short grass, a few distant trees on the horizon, light hazy summer sky at the top. Painterly-realistic style, soft diffused daylight from the upper left, no harsh shadows. Muted, slightly desaturated palette, low contrast, soft atmospheric haze, matte finish, gentle pastel-leaning greens, no deep blacks, no bright highlights — the image must stay calm and recede into the background because game pieces will be drawn on top of it. Detail spread evenly across the whole width with no single focal point. The top 15% and bottom 15% of the image are simple and low-detail (plain soft sky at top, plain soft grass at bottom) so the image can blend into neighbouring images. Composition: an ultra-wide panoramic strip. Keep all the important scenery inside the middle horizontal band (about the middle half of the image height); the upper and lower parts are only extra sky and ground that will be cropped away. No text, no people, no animals, no snakes, no ladders, no frames, no borders. Generate the image in the widest landscape format you can (ideally 3:1).
```

## 2. מדבר (שורות 4–6, משבצות 61–120)

```
Create an image: a wide panoramic realistic desert landscape with smooth golden sand dunes and fine wind ripples, a few scattered saguaro cacti and small desert rocks, warm hazy sky with a soft low sun glow at the top. Painterly-realistic style, soft diffused daylight from the upper left, no harsh shadows. Muted, slightly desaturated palette, low contrast, soft atmospheric haze, matte finish, gentle sandy beige and soft ochre tones, no deep blacks, no bright highlights — the image must stay calm and recede into the background because game pieces will be drawn on top of it. Detail spread evenly across the whole width with no single focal point. The top 15% and bottom 15% of the image are simple and low-detail (plain soft sky at top, plain smooth sand at bottom) so the image can blend into neighbouring images. Composition: an ultra-wide panoramic strip. Keep all the important scenery inside the middle horizontal band (about the middle half of the image height); the upper and lower parts are only extra sky and ground that will be cropped away. No text, no people, no animals, no snakes, no ladders, no frames, no borders. Generate the image in the widest landscape format you can (ideally 3:1).
```

## 3. ג'ונגל (שורות 7–9, משבצות 121–180)

```
Create an image: a wide panoramic realistic tropical jungle scene, lush layered foliage with large monstera and palm leaves, hanging vines, a few soft tropical flowers, filtered light through the canopy, light misty air. Painterly-realistic style, soft diffused daylight from the upper left, no harsh shadows. Muted, slightly desaturated palette, low contrast, soft atmospheric haze, matte finish, soft emerald and sage greens, no deep blacks, no bright highlights — the image must stay calm and recede into the background because game pieces will be drawn on top of it. Detail spread evenly across the whole width with no single focal point. The top 15% and bottom 15% of the image are simple and low-detail (soft misty canopy at top, soft mossy ground at bottom) so the image can blend into neighbouring images. Composition: an ultra-wide panoramic strip. Keep all the important scenery inside the middle horizontal band (about the middle half of the image height); the upper and lower parts are only extra sky and ground that will be cropped away. No text, no people, no animals, no snakes, no ladders, no frames, no borders. Generate the image in the widest landscape format you can (ideally 3:1).
```

## 4. ארקטי (שורות 10–12, משבצות 181–240)

```
Create an image: a wide panoramic realistic arctic landscape, snow-covered mountain range in the middle distance, snowy pine trees, smooth snowfields, light gently falling snow, a faint soft aurora in a pale blue sky at the top. Painterly-realistic style, soft diffused daylight from the upper left, no harsh shadows. Muted, slightly desaturated palette, low contrast, soft atmospheric haze, matte finish, soft icy blues and gentle greys, snow kept off-white rather than glaring pure white, no deep blacks, no bright highlights — the image must stay calm and recede into the background because game pieces will be drawn on top of it. Detail spread evenly across the whole width with no single focal point. The top 15% and bottom 15% of the image are simple and low-detail (plain soft sky at top, plain smooth snow at bottom) so the image can blend into neighbouring images. Composition: an ultra-wide panoramic strip. Keep all the important scenery inside the middle horizontal band (about the middle half of the image height); the upper and lower parts are only extra sky and ground that will be cropped away. No text, no people, no animals, no snakes, no ladders, no frames, no borders. Generate the image in the widest landscape format you can (ideally 3:1).
```

## 5. חלל (שורות 13–15, משבצות 241–300)

```
Create an image: a wide panoramic realistic deep-space scene with soft purple and blue nebulae, a distant spiral galaxy, a ringed planet and one or two small planets, a dense field of fine stars. Painterly-realistic style, soft even lighting. Muted, slightly desaturated palette, low contrast, soft glow, matte finish, deep muted navy and indigo tones instead of pure black, no harsh bright highlights or lens flares — the image must stay calm and recede into the background because game pieces will be drawn on top of it. Detail spread evenly across the whole width with no single focal point. The top 15% and bottom 15% of the image are simple and low-detail (sparse stars only) so the image can blend into neighbouring images. Composition: an ultra-wide panoramic strip. Keep all the important scenery inside the middle horizontal band (about the middle half of the image height); the upper and lower parts are only extra sky and ground that will be cropped away. No text, no people, no astronauts, no spaceships, no snakes, no ladders, no frames, no borders. Generate the image in the widest landscape format you can (ideally 3:1).
```

---

**Negative prompt** (לכלים שתומכים בו, למשל Stable Diffusion או Firefly. ב-Midjourney כותבים `--no` ואחריו הרשימה):

```
text, letters, watermark, logo, frame, border, people, animals, snakes, ladders, high contrast, oversaturated, neon, harsh shadows, lens flare, pure black, blown-out highlights, central focal point
```
