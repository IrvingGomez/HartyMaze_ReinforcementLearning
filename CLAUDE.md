We are going to solve a mouse maze using Iterative Policy Improvement.

MouseMaze shows the maze that we are going to solve. However, there are some changes that we will introduce:

1. Change the cheese for the Treasure.png in the image folder.
2. We are going to introduce a chracter called "Harty", its image is in harty.png in the image folder.
3. Currently I have an image of Harty looking to the right that is what we are going to introduce in the maze.

4. To use Iterative Policy Improvement I have codified the cells of the maze accordint to the next rules:

Each cell has been coded through a number from 0 to 14 as:
0: left, and top walls, 1: top wall, 2: right and top wall, 3: left wall, 4: no walls, 5: right wall, 6: left and bottom wall, 7: bottom wall, 8: right and bottom wall, 9: left, bottom, and right wall, 10: top, right, and bottom wall, 11: top, left, and bottom wall, 12: top, left, and right wall, 13: top, and bottom wall, 14: left and right wall.

From this coding, the MouseMaze can be coded as:
[
    [0,13,2,12,11,2,11,2,0,2],
    [14,11,8,6,2,6,13,5,9,14],
    [6,13,1,1,5,0,13,8,0,8],
    [12,0,8,14,9,6,13,13,5,12],
    [6,8,0,7,2,11,13,2,6,5],
    [0,2,6,2,6,2,0,8,12,14],
    [14,6,13,8,12,6,8,0,7,8],
    [6,2,0,13,8,11,2,6,13,2],
    [0,8,3,10,0,2,3,1,10,14],
    [6,13,7,13,8,6,8,6,13,8]
]

5. I have already a code 04_GridWorldMouseMaze_V4.ipynb which implements the Iterative Policy Improvement. DO NOT modify this file.
6. The user can choose the position to put the treasure (called cheese in 04_GridWorldMouseMaze_V4.ipynb), and I want to add that the user also adds a position for Harty in the maze, the user can also selects the value of the discount rate.

## The goal

The goal of this project is to introduce Iterative Policy Improvement for high schoolers, so it hsa to be fun and simple.

## Rules for coding

1. DO NOT overengineer, keep it simple
2. No emojis in code, docs, commits, or any other place
3. DO NOT use a defensive programming.
4. Make it ina  way that is human readible, let's create functions when possible to make it more modular. Right now, the functions doing everything in 04_GridWorldMouseMaze_V4.ipynb are too large and confusing for a human.
5. Use Python
6. Use latest versions of libraries and idiomatic approaches as of today

## Future objectives

Keep in mind that later I want to implement this:

1. The possibility to make a video showing how Harty moves through the maze. Thus, you need to complement the HartyMaze_right.png image with Harty looking ro the left, up, and down.

2. The user can see through the video how Harty follows teh policy. Thus, something that could be done is to plot the policy on the left, and Harty moving through the maze on the right.

## Working documentation

All documents for planning and executing this project will be in the docs/ directory.
Please review the docs/PLAN.md document before proceeding.

## Limitation

1. Right now we are not building any UI, no frontend, no deployment, no webpage