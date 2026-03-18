## Since before

Since the previous article, I have implemented a lot of graphics techniques and expanded it functionality. From being able
to load `.glTF` file for more complicated scenes (with triangle clipping), to LTC area light, PBR shading and transmissive materials. It allowed me to render cool scenes
made by cool artists like `The Junk Shop`:

![Junkshop Scene](../assets/junkshop_final.png)

and modern sample assets such as `Lumberyard Bistro`:

![Bistro Scene](../assets/pointlight.png)

ensuring HDR screens are not wasted:

![Damaged Helmet](../assets/0_helmet.avif)

> Make sure your browser supports `.avif` file, or your screen supports HDR content

I haven't written much for it, other than simple [project page](zigcpurasterizer.html) as part of portflio. The reason for that is simple:

- There wasn't anything worth documenting that wouldn't be found by simple google search or something that people haven't already wrote 1000s of words about it.

As I am satisfied with the visual quality I have achieved for a CPU software rasterizer, I wanted to chase performance, hoping to getting in range of real-time (~50ms) rendering for midly complex scene. This is what majority of post is about.

## Frustrum Culling

Clip-space is defined by multiplying vertex/point with View-Project (VP) matrix.

In clip-space, its volume is defined by,

```md
 -Wc <= Xc/Yc/Zc <= Wc, where Pc = (Xc, Yc, Zc, Wc) is a point in clip-space
```

and its 6 planes are,

```md
-> -Wc <= Xc  = Left Plane
->  Xc <= Wc  = Right Plane
-> -Wc <= Yc  = Top Plane
->  Yc <= Wc  = Bottom Plane
-> -Wc <= Zc  = Near Plane
->  Zc <= Wc  = Far Plane
```

if we re-arrange them, we get

```md
-> Wc + Xc >= 0  = Left Plane
-> Wc - Xc >= 0  = Right Plane
-> Wc + Yc >= 0  = Top Plane              (EQ-0)
-> Wc - Yc >= 0  = Bottom Plane
-> Wc + Zc >= 0  = Near Plane
-> Wc - Zc >= 0  = Far Plane
```

Now, consider matrix multiplication of `VP` matrix and a world space point `P` to get clip-space point `Pc`,

```md
-> Pc = VP * P
```

Let represent VP matrix by rows,

```md
->
     | Row0 |   | X |
Pc = | Row1 | * | Y | , where RowN represent each row of VP matrix
     | Row2 |   | Z |
     | Row3 |   | W |

```

results in,

```md
-> Xc = Row0 * P
-> Yc = Row1 * P            (EQ-1)
-> Zc = Row2 * P
-> Wc = Row3 * P
```

Substituting `EQ-1` in `EQ-0`, we get

```md
-> (Row3 * P) + (Row0 * P) >= 0  = Left Plane
-> (Row3 * P) - (Row0 * P) >= 0  = Right Plane
-> (Row3 * P) + (Row1 * P) >= 0  = Top Plane
-> (Row3 * P) - (Row1 * P) >= 0  = Bottom Plane
-> (Row3 * P) + (Row2 * P) >= 0  = Near Plane
-> (Row3 * P) - (Row2 * P) >= 0  = Far Plane
```

re-arranging them, we get

```md
-> (Row3 + Row0) * P >= 0  = Left Plane
-> (Row3 - Row0) * P >= 0  = Right Plane
-> (Row3 + Row1) * P >= 0  = Top Plane
-> (Row3 - Row1) * P >= 0  = Bottom Plane
-> (Row3 + Row2) * P >= 0  = Near Plane
-> (Row3 - Row2) * P >= 0  = Far Plane
```

Looks similar? It vector equation for each plane. Consider `Left Plane`, let expand `Row3` and `Row0`

```txt
-> Row0 = (VP_00, VP_01, VP_02, VP_03)
-> Row3 = (VP_30, VP_31, VP_32, VP_33)

-> Row3 + Row0 = (VP_30 + VP_00, VP_31 + VP_01, VP_32 + VP_02, VP_33 + VP_03)
```

Lets rename each components

```txt
-> A = VP_30 + VP_00
-> B = VP_31 + VP_01
-> C = VP_32 + VP_02
-> D = VP_33 + VP_03
```

If we do dot product of `(Row3 + Row0) = (A, B, C, D)` with `P = (X, Y, Z, 1)` we get

```txt
AX + BY + CZ + D >= 0
```

Which is general equation of plane. A, B, C would represent normal and D the distance. Pseudocode would look like:

```py
def extractPlanes(view_projection_matrix):
	row0 = view_projection_matrix.row0()
	row1 = view_projection_matrix.row1()
	row2 = view_projection_matrix.row2()
	row3 = view_projection_matrix.row3()
	
	planes = [
		Vec4.add(row3, row0), # Left Plane
		Vec4.sub(row3, row0), # Right Plane
		Vec4.add(row3, row1), # Top Plane
		Vec4.sub(row3, row1), # Bottom Plane
		Vec4.add(row3, row2), # Near Plane
		Vec4.sub(row3, row2) # Far Plane
	]
	
	for plane in planes:
		len = sqrt(plane.x * plane.x + plane.y * plane.y + plane.z * plane.z)
		plane.x /= len
		plane.y /= len
		plane.z /= len
		plane.w /= len
	
	return planes
```

---

There are multiple kind of bounding structures:

- Bounding Sphere
- Axis-Aligned Bounding Box (AABB)
- Oriented Bounding Box (OBB)
- Convex Hull

Among the fastest is Bounding Sphere and then AABB, but among the best bounded is OBB and Convex Hull. Each of them have their own use. For rasterizer need, we want to be able to quickly discard the object if it entirely out of frustrum, and since our rasterizer has software triangle clipping (which can be a bottleneck) we want to do it only on objects intersecting the plane. So, we want the culling test to be fast with structure compact enough to minimize triangle clipping. Bounding Sphere and AABB are probably good enough for it.

To test sphere and plane intersection, we plug sphere's center into plane equation (sphere represented with center `S` and radius `R`):

```txt
ASx + BSy + CSz + D = 0
```

For each plane, we get three cases:

```txt
->       ASx + BSy + CSz + D > R   , completely inside the frustrum
->       ASx + BSy + CSz + D < -R  , completely outside the frustrum
-> R <= ASx + BSy + CSz + D <= -R  , intersecting the frustrum
```

psuedocode would look something like:

```py

def testBoundingSphere(planes, sphere):
	count = 0
	for plane in planes:
		n = plane.vec3()
		d = plane.w
		distance = Vec3.dot(n, sphere.center) + d
		
		if distance < -sphere.radius:
			return "Outside"
		if distance > sphere.radius:
			count += 1
	
	if count == 6:
		return "Inside"
	else:
		return "On-plane"
```

Culling test for AABB isn't much more complicated, though it little bit more computationally expensive. AABB can be represent in multiple ways, we represent it as Center `C` + Extent `E` (size). This way we can get each point and only store 6 floats. Test is straight forward, check if each point is "inside" the plane.

Example for one of the point if it completely inside:

```txt
-> x = Cx + Ex
-> y = Cy + Ey
-> z = Cz + Ez

-> P = (x, y, z)

-> (n * P) + d <= 0
```

in pseudocode it translate to:

```py
def testAABB(planes, aabb):
	plane_count = 0
	for plane in planes:
		count = 0
		n = plane.vec3()
		d = plane.w
		p = Vec3(aabb.c.x + aabb.e.x, aabb.c.y + aabb.e.y, aabb.c.z + aabb.e.z)
		if(Vec3.dot(n, p) + d > 0):
			count++
		p = Vec3(aabb.c.x - aabb.e.x, aabb.c.y + aabb.e.y, aabb.c.z + aabb.e.z)
		if(Vec3.dot(n, p) + d > 0):
			count++
		p = Vec3(aabb.c.x + aabb.e.x, aabb.c.y - aabb.e.y, aabb.c.z + aabb.e.z)
		if(Vec3.dot(n, p) + d > 0):
			count++
		p = Vec3(aabb.c.x + aabb.e.x, aabb.c.y + aabb.e.y, aabb.c.z - aabb.e.z)
		if(Vec3.dot(n, p) + d > 0):
			count++
		p = Vec3(aabb.c.x - aabb.e.x, aabb.c.y - aabb.e.y, aabb.c.z + aabb.e.z)
		if(Vec3.dot(n, p) + d > 0):
			count++
		p = Vec3(aabb.c.x + aabb.e.x, aabb.c.y - aabb.e.y, aabb.c.z - aabb.e.z)
		if(Vec3.dot(n, p) + d > 0):
			count++
		p = Vec3(aabb.c.x - aabb.e.x, aabb.c.y + aabb.e.y, aabb.c.z - aabb.e.z)
		if(Vec3.dot(n, p) + d > 0):
			count++
		p = Vec3(aabb.c.x - aabb.e.x, aabb.c.y - aabb.e.y, aabb.c.z - aabb.e.z)
		if(Vec3.dot(n, p) + d > 0):
			count++
		
		if(count == 0):
			return "Outside"
		if(count == 8):
			plane_count++
	
	if(plane_count == 6):
		return "Inside"
	else:
		return "On-plane"
```

Computationally, the AABB test is more expensive but if it culls better than sphere, better enough to reduce more pressure on culling test compared to sphere, than AABB should be faster. 

### Implementation

Here we have total object count, and "on-plane" object count for each bounding structure. Lower "on-plane" object count is better.

| Scene-Camera | Total | Sphere (on-plane) | Sphere % (on-plane) | AABB (on-plane) | AABB % (on-plane) |
|:-------------|------:|------------------:|--------------------:|----------------:|------------------:|
| JunkShop-1   |    78 |     58 | 74.36 % |  50 |  64.1 % |
| JunkShop-2   |    78 |     48 | 61.54 % |  36 | 46.15 % |
| Bistro-1     |  2909 |    176 |  6.05 % | 144 |  4.95 % |
| Bistro-2     |  2909 |    258 |  8.87 % | 188 |  6.46 % |
| Bistro-3     |  2909 |    268 |  9.21 % | 196 |  6.74 % |
| Bistro-4     |  2909 |    210 |  7.22 % | 150 |  5.16 % |
| Bistro-5     |  2909 |    157 |   5.4 % | 108 |  3.71 % |
| Tavern-1     |    69 |     62 | 89.86 % |  62 | 89.86 % |
| Tavern-2     |    69 |     66 | 95.65 % |  62 | 89.86 % |

![](../assets/junkshop_objects.png)
![](../assets/bistro_objects.png)
![](../assets/tavern_objects.png)

We can see AABB consistently perform better than sphere when it culling as accurately as possible and leaving less objects on plane for triangle clipping. This must mean we can also expect timing to be better for AABB, right?

#### Bistro Timings

Lets take a look at Bistro scene, it's sample asset that is large enough to make difference with frustrum culling. We have timings with Bounding Sphere:

| Scene-Camera | Before (ms) | Sphere (ms) |	Diff (ms)	|     SE Diff (ms) |	Improvement (%) |
|:-------------|------------:|------------:|-----------:|-----------------:|-----------------:|
| Bistro-1     |        2126 |        1894 |        232 |             4.56 |          10.91 % |
| Bistro-2     |        2237 |        2001 |        236 |              5.9 |          10.55 % |
| Bistro-3     |        2138 |        1911 |        227 |             6.31 |          10.62 % |
| Bistro-4     |        2880 |        2580 |        300 |             7.95 |          10.42 % |
| Bistro-5     |        2554 |        2274 |        280 |             6.12 |          10.96 % |

The difference between before and after sphere frustrum culling is loud and clear, with improvement consistently around ~10.5%. The timing is well above its standard error of difference `SE Diff` so we know improvement isn't noise, but very real optimization. So, atleast sphere frustrum culling isn't useless.

Now lets see AABB frustrum culling performance:

| Scene-Camera | Before (ms) | AABB (ms) | Diff (ms) |     SE Diff (ms) | Improvement (%) |
|:-------------|------------:|----------:|----------:|-----------------:|----------------:|
| Bistro-1     |        2126 |      1911 |       215 |             2.87 |           10.11 |
| Bistro-2     |        2237 |      1989 |       248 |             4.33 |           11.09 |
| Bistro-3     |        2138 |      1907 |       231 |             6.15 |            10.8 |
| Bistro-4     |        2880 |      2632 |       248 |              2.6 |            8.61 |
| Bistro-5     |        2554 |      2283 |       271 |             2.36 |           10.61 |

We can say the same here, performance is very real with upto 11.09% improvement.

![](../assets/bistro_timing.png)

Now lets compare, both method and see which is actually better.

- `Bistro-4`: Sphere (2580 ms) beats AABB (2632 ms), their difference (52 ms) is well above their SE Diff (7.95 ms and 2.6 ms).
- `Bistro-1`: Sphere (1894 ms) beats AABB (1911 ms), their difference (17 ms) is above their SE Diff (4.56 ms and 2.87 ms).
- `Bistro-5`: Sphere (2274 ms) barely beats AABB (2283 ms), their difference (9 ms) is slightly above their SE Diff (6.12 ms and 2.36 ms).
- `Bistro-2`: AABB (1989 ms) beats Sphere (2001 ms), their difference (12 ms) is above their SE Diff (4.33 ms and 5.9 ms).
- `Bistro-3`: Its a tie between AABB (1907 ms) and Sphere (1911 ms), their difference (4 ms) is lower their SE Diff (6.15 ms and 6.31 ms).

![](../assets/bistro_timing_comp.png)

From what we see above, Sphere frustrum culling appears to be somewhat better than AABB. Only in `Bistro-2` AABB win with some difference, while in `Bistro-3` AABB win is within margins of error.

#### The Junk Shop Timings

Sphere frustrum culling timings:

| Scene-Camera | Before (ms) | Sphere (ms) | Diff (ms) | SE Diff (ms) | Improvement (%) |
|:-------------|------------:|------------:|----------:|-------------:|----------------:|
| JunkShop-1   |        2458 |        2263 |       195 |         4.72 |            7.93 |
| JunkShop-2   |        2016 |        1814 |       202 |         5.72 |           10.02 |

AABB frustrum culling timings:

| Scene-Camera | Before (ms) | AABB (ms) | Diff (ms) | SE Diff (ms) | Improvement (%) |
|:-------------|------------:|----------:|----------:|-------------:|----------------:|
| JunkShop-1   |	      2458 |      2275 |       183 |          7.6 |	           7.45 |
| JunkShop-2   |	      2016 |      1810 |       206 |         5.23 |	          10.22 |

Even though the object culling count isn't as stellar as `Bistro` scene, rejection of fewer but higher poly mesh has contributed to higher improvement.

![](../assets/junkshop_timing.png)

If we compare both methods, we can see:

- `JunkShop-1`: Sphere (2263 ms) beats AABB (2275 ms), their difference (12 ms) is above their SE Diff (4.72 ms and 7.6 ms).
- `JunkShop-2`: Its a tie between AABB (1810 ms) and Sphere (1814 ms), their difference (4 ms) is below their SE Diff (5.23 ms and 5.72 ms).

![](../assets/junkshop_timing_comp.png)

Sphere culling again appears to be slightly better than AABB.

#### Tavern Timings

Sphere frustrum culling timings:

| Scene-Camera | Before (ms) | Sphere (ms) | Diff (ms) | SE Diff (ms) | Improvement (%) |
|:-------------|------------:|------------:|----------:|-------------:|----------------:|
| Tavern-1     |         588 |         579 |         9 |         2.09 |            1.53 |
| Tavern-2     |         681 |         677 |         4 |         2.14 |            0.59 |

AABB frustrum culling timings:

| Scene-Camera | Before (ms) | AABB (ms) | Diff (ms) | SE Diff (ms) | Improvement (%) |
|:-------------|------------:|----------:|----------:|-------------:|----------------:|
| Tavern-1     |         588 |       575 |        13 |          2.1 |            2.21 |
| Tavern-2     |         681 |       668 |        13 |         1.88 |            1.91 |

Although very small, there is real improvement in speed.

![](../assets/tavern_timing.png)

In both of the camera, AABB wins against Sphere:

- `Tavern-1`: AABB (575 ms) beats Sphere (579 ms), their difference (4 ms) is above then their SE Diff (2.09, 2.1).
- `Tavern-1`: AABB (668 ms) beats Sphere (677 ms), their difference (9 ms) is above then their SE Diff (2.14, 1.88).

![](../assets/tavern_timing_comp.png)
