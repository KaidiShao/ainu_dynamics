---
asset_id: MC_BODY_REF_001D
character: 马尔切洛·卡瑞洛
asset_type: provisional_body_reference
generation_date: 2026-07-17
tool_mode: built_in_image_gen
identity_anchor: MC_FACE_REF_001
body_direction_source: MC_BODY_REF_001C_text_only
status: rejected_body_mass_and_hand_drift
body_anchor_status: not_established
identity_anchor_effect: none
sha256: 63C743408FD9B0649D5C2FD860BCB3CC9AA23A30574ACBC9CE5D615504838718
---

# MC_BODY_REF_001D｜第三体量方向的正面承重修正

## 1. 作者反馈与本轮目的

作者对第一轮的判断为：

- 三张体态均有怪异感；
- 若只看身体方向，第三张相对更接近卡瑞洛；
- 需要保留第三张的肩腰比例、胸背容量与整体重量感，但不能继承第三张已经漂移的脸。

因此，本轮只生成一张正面技术参考，优先修正：

- 双脚与地面的关系；
- 膝盖是否锁死；
- 重心是否真实落在身体里；
- 骨盆与胸廓是否垂直叠放；
- 肩膀、手肘与手指是否自然受重力影响；
- 裤腰是否回到自然腰，避免高腰长腿幻觉。

## 2. 输入与继承关系

图像输入只有：

```text
MC_FACE_REF_001
01_卡瑞洛/01_原始参考/MC_FACE_REF_001_冷战后期克制请求_原图.jpg
```

`MC_BODY_REF_001C`没有作为图像输入。其可取身体部分只被转写为文字：

- 高而偏修长，但不显得脆弱；
- 肩部只比骨盆略宽；
- 胸廓与上背具有中等容量；
- 腰线较直，不形成夸张倒三角；
- 颈肩细而连贯；
- 有长期功能性训练痕迹，但不健身化。

本轮结果不得继承或重写原图的脸，也不得使第一轮 C 从 `REJECTED_IDENTITY_DRIFT` 恢复为可用图像。

## 3. 完整生成提示词

```text
Use case: identity-preserve
Asset type: provisional character body-proportion technical reference,
corrected front-view test; not a costume image and not a power portrait.

Input image:
Image 1 is the sole and exclusive facial identity anchor.
Preserve this exact person's recognizable face:
the same longish facial structure, eyebrow and eye spacing, eye shape,
clear nose bridge and nose proportions, restrained lip shape,
cheekbones, jawline, age impression, slight natural asymmetry,
deep brown near-black naturally wavy hair, subdued blue-gray eyes,
and warm ivory Southern European skin direction.
Use Image 1 only for facial identity.
Do not inherit any previously generated body image, face, pose,
clothing, lighting, or background.

Primary request:
Create a new photorealistic full-body front technical reference
of the same man, visually consistent with a canonical height of 185 cm.
Use the preferred third body direction translated into text only:
a tall, moderately lean adult build;
natural shoulders only modestly wider than the pelvis;
moderate chest depth and stable upper-back capacity;
no square padded shoulder line;
a straight firm waist without a tiny V-shaped taper;
proportionate long limbs;
a slim but integrated neck-to-shoulder relationship;
understated evidence of long-term functional training.
He should feel grounded, elegant, and physically capable,
not bulky, gym-sculpted, fragile, or model-thin.

Posture and weight mechanics:
Strict front view with the body facing the camera,
but not a fashion pose or military attention.
Feet hip-width apart and nearly parallel,
both soles fully on the same floor plane;
one foot only 2–3 cm ahead.
Knees softly unlocked.
Weight distributed approximately 55/45
with a very subtle natural preference to one leg,
without hip jut, crossed legs, contrapposto, S-curve, or visible lean.
Pelvis neutral and level.
Ribcage vertically stacked over the pelvis after a quiet exhale,
with no chest thrust.
Spine naturally upright.
Shoulders relaxed downward and nearly level,
not pulled back or squared.
Upper arms hang naturally 3–5 cm away from the torso,
elbows softly unlocked, forearms following gravity,
wrists neutral, fingers separated and gently curved.
Head centered over the sternum;
chin exactly level;
neck neither stretched nor compressed.

Clothing:
Ordinary matte charcoal-gray long-sleeve cotton shirt
with a standard collar, only the top button open,
regular fit with realistic ease through chest, waist,
sleeves and armholes; not tight and not oversized.
Neatly tucked without pulling into plain dark straight-leg trousers
worn at the natural waist, neither high-rise nor low-rise.
Minimal unbranded dark shoes.
No jacket, knitwear, tie, jewelry, watch, decorative belt,
weapon, logo, or styling prop.

Scene/backdrop:
Empty seamless warm-neutral gray studio
with a clearly visible flat floor plane
and a soft contact shadow directly beneath both shoes;
no furniture or objects.

Composition/framing:
Portrait full-body reference, exact frontal camera axis;
entire head, both hands, both legs and both shoes visible
with generous equal margins.
Both shoes should be at nearly equal distance from the camera
so neither is enlarged.
Camera absolutely level at approximately lower-chest height,
placed far enough away for a natural 85–105 mm
full-length portrait perspective.
No low angle, high angle, wide-angle distortion, tilted horizon,
compressed torso, elongated legs, oversized feet,
high-waist illusion, or tiny head.

Expression/gaze:
Quiet, attentive and cognitively present;
relaxed brow and jaw;
neutral closed mouth;
stable gaze toward a specific person just beside the lens.
No smile, smirk, pleading, squint, glare, seduction,
blank mannequin expression, lifted chin,
or downward dominance gaze.

Lighting/mood:
Soft even neutral studio daylight, low contrast,
realistic pores, hair and fabric grain;
no glamour retouching, cinematic rim light,
dramatic shadow, or editorial fashion mood.

Constraints:
Prioritize believable gravity and anatomical alignment
over elegance or posing.
The body should look like a real person simply standing still
after an exhale.
Preserve facial identity aggressively.
Keep hands anatomically correct, shoulders natural,
pelvis level, trouser waist natural,
and shirt folds consistent with the stated weight distribution.
This remains PROVISIONAL and must not establish
permanent face, side profile, or body canon.

Avoid:
identity drift;
a different but similar handsome man;
generic AI male model;
altered eyes, nose, lips, jaw or age;
bright ice-blue eyes;
Nordic cold-white skin;
over-symmetrization;
raised chin;
head tilt;
mannequin stiffness;
fashion contrapposto;
hip jut;
locked knees;
one shoulder lifted;
chest thrust;
arms pinned rigidly to the sides;
hands posed for a catalog;
widened shoulders;
inverted-triangle torso;
bodybuilder chest or arms;
tiny waist;
high-waisted long-leg distortion;
oversized hands or shoes;
heroic, mafia, bodyguard, old-money or runway styling;
low camera;
text;
labels;
watermark.
```

## 4. 作者最终裁决

作者确认该图存在以下问题：

- 体量偏胖、偏魁梧；
- 肩胸、上臂和大腿同时增厚；
- 体态不够舒展；
- 手掌偏宽、偏厚；
- 手指不够修长。

该反馈与既有“修长、骨节清楚、稳定而有力量”的手部设定冲突，也使身体接近以体量表现危险的禁区。

因此，本图改判为：

```text
REJECTED_BODY_MASS_AND_HAND_DRIFT
NEGATIVE_REFERENCE
NOT_BODY_ANCHOR
NOT_IDENTITY_ANCHOR
```

本图不得继续派生。后续只继承其失败教训：删除容易被模型翻译成宽肩、厚胸和粗手臂的体量词，并单独约束窄掌、长指与舒展体态。

## 5. 文件校验

```text
文件：02_修正轮次/MC_BODY_REF_001D_第三体量方向_正面承重修正_AUTHOR_REVIEW_PENDING.png
尺寸：941×1672
大小：1,632,753 bytes
SHA-256：63C743408FD9B0649D5C2FD860BCB3CC9AA23A30574ACBC9CE5D615504838718
```
