1. Genome Assembly in 3 stages:
   1. A pre-constructed list of error-free reads is parsed to perform the task of Genome Assembly by constructing an overlap graph: two reads are joined by a directed edge of weight equal to the length of the maximum overlap of these two reads. We then construct a Hamiltonian path in this graph in a greedy manner.
   2. The second stage detects Eulerian cycles by assuming that there are no isolated vertices in a graph. A graph contains an Eulerian cycle if and only if it is strongly connected and for each vertex, its in-degree is equal to its out-degree. 
   3. The last part of the solution is similar to solving the maximum flow problem, with the aim of trying to assign a flow to each edge satisfying capacity and conservation criteria.
2. Image compression using Discrete Cosine Transform: This MATLAB code performs several image processing tasks:
    1.	Reads an image specified by the user, displays it, and converts it to grayscale.
    2.	Converts the grayscale image back to RGB and displays it.
    3.	Plots the histogram of the grayscale image.
    4.	Resizes the image based on user input.
    5.	Implements a DCT-based image compression algorithm on the resized image.
    6.	Displays the compressed image and saves it as a JPEG file with a filename indicating the compression factor.
3. Analog Communication project - Bluetooth Home Automation
4. Digital Communication-MATLAB codes
