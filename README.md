# PyCellFIT
<<<<<<< HEAD
> Author: XJ Xu
> A web-based application of [CellFIT](http://journals.plos.org/plosone/article?id=10.1371/journal.pone.0099116) ([Wayne Brodland](http://www.civil.uwaterloo.ca/brodland/cellFIT.asp)'s web page)

#### Brief description:
CellFIT is a package of force inference equations and assessment tools that calculates the forces in cell edges based on their geometries. In this approach, cells in an image are segmented and equilibrium equations are constructed for each triple junction based solely on edge tensions and the angles at which edges approach each junction. Solving the resulting system of tension equations yields a set of relative edge tensions whose scaling must be determined from data external to the image.
In this implementation, the goal is to optimize the user interface for improved accessibility of CellFIT to scientists of all backgrounds across all platforms (Linux, MacOS, Windows). 
Applying this tool to the cell mechanics of wound healing is of particular interest.

<!--- [Young-Laplace Equation](https://en.wikipedia.org/wiki/Young%E2%80%93Laplace_equation)--->

#### Full description:



=======
### Author: XJ Xu

![Cell layer](/images/fem_vis.png)
![Dragonfly wing](/images/dragonfly_wing.png)

CellFIT is a package of force inference equations and assessment tools that calculates the forces in cell edges based on their geometries. In this approach, cells in an image are segmented and equilibrium equations are constructed for each triple junction based solely on edge tensions and the angles at which edges approach each junction. Solving the resulting system of tension equations yields a set of relative edge tensions whose scaling must be determined from data external to the image.

Given an image of an epithelial cell sheet, CellFIT can infer cellular forces by segmenting the image into individual cells, constructing equilibrium equations for the points where cells meet at triple junctions, and finding a least-squares solution for the tensions at cell­cell interfaces. Similarly, cellular pressures can be estimated by constructing Laplace equations that relate the edge tensions, curvatures and cellular pressure differences. Despite these capabilities, the accessibility of CellFIT to scientists of all backgrounds is not yet optimized. I am working on an updated web­based application of CellFIT that allows users to access the software from a browser. The updated version would include improved error handling and the implementation of additional functionality for reading and processing image stacks. I hope to apply the web-based CellFIT to time-resolved image stacks of wound healing in Drosophila epithelia to demonstrate spatial and temporal variations in cellular forces as the wounds close.
>>>>>>> 69b2f22049f29b6c6ab2c2ce81350af7bc180ad7
