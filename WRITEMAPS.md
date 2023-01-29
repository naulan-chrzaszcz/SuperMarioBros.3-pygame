Wrote by Naulan CHRZASZCZ
# How to write a map
First, you use a simple `txt` file
-- --
## Without header
You'll begin to write your map data directly on the first line
```txt
111,-1,-1,-1
214,-1,-1,-1
```
## With header
You'll use the first line to attributes (separated by `;`) and you'll begin to write you map data on the second line
```txt
attribute:something;other_attribute:other_something
111,-1,-1,-1
214,-1,-1,-1
```
### The attributes
- **type_of_map**
  - 1: meaning STAGE
  - 2: meaning LEVEL

⚠️ ️**You need to haven't any whitespace like this on each virgule `1, 1` but prefer like this `1,1`**
-- --
## Tiles data
- **first number:**
define the block
- **second number:**
define where look up
- **last number:**
define colors of texture