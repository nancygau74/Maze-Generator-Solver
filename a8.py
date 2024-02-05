import heapq
import random

import png
from PIL import Image, ImageDraw, ImageFont

class Grid:
    def __init__(self, num_rows, num_cols):
        self.rows = None
        self.num_rows = num_rows
        self.num_cols = num_cols

        self.prepare_grid()
        self.configure_cells()

    ## Populate the rows with cells
    def prepare_grid(self):
        #Create 2D array of Cells
        self.rows = [[] for i in range(self.num_rows)]
        for row in range(self.num_rows):       #parse row
            for col in range(self.num_cols):   #parse column
                cell = Cell(row,col)
                self.rows[row].append(cell)

    def get_cell(self, which_row, which_col):
# If either which_row or which_col is invalid (negative or greater than the number of
#   rows or cols), return None.
        if which_row >= self.num_rows or which_row < 0 or which_col >= self.num_cols or which_col < 0 :
            return None
#return the cell at the given location
        return self.rows[which_row][which_col]
    def configure_cells(self):
        #Tell all the cells who their neighbors are
        for row in self.rows:
            for cell in row:
                #print("cell index:", cell.row,cell.col)
                if cell.row != 0:               #North
                    cell.set_neighbor(cell.NORTH, self.get_cell(cell.row -1, cell.col))
                if cell.col != 0:               #West
                    cell.set_neighbor(cell.WEST, self.get_cell(cell.row, cell.col-1))
                if cell.row != self.num_rows-1:   #South
                    cell.set_neighbor(cell.SOUTH, self.get_cell(cell.row+1, cell.col))
                if cell.col != self.num_cols-1:   #East
                    cell.set_neighbor(cell.EAST, self.get_cell(cell.row, cell.col +1))

    ## This may not be used; depends on what Maze algorithms we end up implementing!
    """Return a random cell"""
    def random_cell(self):
        pass

    """Return how many cells are in this grid"""
    def size(self):
        return len(self.all_cells())

    """Returns a flattened list of all the cells """
    def all_cells(self):
        return [cell for row in self.rows for cell in row]

    def __iter__(self):
        return GridIterator(self)

    """Prints the grid. See the README for some guidance. """
    def print(self):
        img_row = 2* self.num_rows + 1
        img_col = 4* self.num_cols + 1
        print("\n")
        for r in range(img_row):
            for c in range(img_col):
                if r == 0 or r == img_row-1:  #print 1st & last row
                    #print("r:",r,"c:",c)
                    if c%4 == 0 and c!=img_col-1:
                        print("+",end='')
                    elif c==img_col-1:
                        print("+")
                    else:
                        print("-",end='')
                    continue
                cur_cell = self.get_cell(int((r-1)/2),int((c-1)/4))
                if r % 2 == 1:
                    if c%4 == 0:
                        if c==0:
                            print("|", end='')
                        elif cur_cell.get_neighbor(cur_cell.EAST) in cur_cell.links: #linked
                            print(" ",end='') #change o to space
                        elif cur_cell.get_neighbor(cur_cell.EAST) == None:
                            print("|")       #last cell in the row
                        else:               #not linked
                            print("|",end='')
                    else:
                        print(" ", end='')  #change 0 to space
                else:   #r%2 == 0 && not 1&last row
                    if c%4==0 and c!=img_col-1:
                        print("+",end='')
                    elif c==img_col-1:
                        print("+")          #last cell in the row
                    elif cur_cell.get_neighbor(cur_cell.SOUTH) in cur_cell.links:  # linked
                        print(" ", end='')
                    elif cur_cell.get_neighbor(cur_cell.SOUTH) not in cur_cell.links:   #not linked
                        print("-", end='')

    def export_image(self, filename = "amaze.png", path = None):
        tile_ht = 50
        tile_wid = 50
        maze_image = Image.new("RGBA", (tile_wid * self.num_cols, tile_ht * self.num_rows), (255, 255, 255,255))
        for which_row, row in enumerate(self.rows):
            for which_col, cell in enumerate(row):
                tile = cell.get_image()
                maze_image.paste(tile, (tile_wid * which_col, tile_ht*which_row))


        if path and len(path) > 1:
            print("Printing the path")
            print(path)
            print("Done printing the path")
            draw = ImageDraw.Draw(maze_image)
            cell1 = path[0]
            for cell2 in path[1:]:
                draw.line((cell1.col * 50 + 15, cell1.row * 50 + 35, cell2.col*50+15, cell2.row *50+ 35), fill=(120,120,117,250), width=8)
                cell1 = cell2

        try:
            maze_image.save("images/" + filename)
        except OSError:
            print("cannot convert", "someatjelsakjr")


class GridIterator:
    def __init__(self, grid):
        self.row_iterator = grid.rows.__iter__()
        self.col_iterator = self.row_iterator.__next__().__iter__()

    def __iter__(self):
        return self

    def __next__(self):
        try:
            return self.col_iterator.__next__()
        except StopIteration:
            ## No more cells in this row; go to the next one
            try:
                self.col_iterator = self.row_iterator.__next__().__iter__()
                return self.__next__() ## Recursive call so we can move on from an empty row
            except StopIteration:
                ## No more rows left to visit
                raise StopIteration

class Cell:
    NORTH = "North"
    SOUTH = "South"
    EAST = "East"
    WEST = "West"
    NEIGHBOR_SETS = [NORTH, SOUTH, EAST, WEST]
    ## Used for the images
    border_color = (175, 176, 178)
    background_color = (117, 128, 156)
    border_width = 6
    text_color = (208,211,212)

    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.neighbor_cells = {} # cell1.NORTH: cell2
        self.links = []        # Which cells are linked to this cell
        self.content = " "
        self.distance = 0 ## Attribute to hold the distance from a source node to this node
        self.visited = 0        #1, when visited in traversing

    def set_neighbor(self, which_neighbor, cell):
        if cell is None:
            pass    # If no cell is provided, do nothing.
        elif which_neighbor in self.NEIGHBOR_SETS:    # which_neighbor must be one of Cell.NORTH, Cell.SOUTH, Cell.EAST, Cell.WEST
                self.neighbor_cells[which_neighbor] = cell
        else:
            raise NotImplementedError                # which_neighbor is not one of these, raise a NotImplementedError

    ## Gets the specified neighbor of this cell
    def get_neighbor(self, which_neighbor):
        if which_neighbor in self.NEIGHBOR_SETS:    # which_neighbor must be one of Cell.NORTH, Cell.SOUTH, Cell.EAST, Cell.WEST
            if which_neighbor not in self.neighbor_cells:
                return None                        # Returns None if the key is valid but no assigned neighbor
            return self.neighbor_cells[which_neighbor]
        else:
            raise NotImplementedError                # which_neighbor is not one of these, raise a NotImplementedError

    ## There is an edge from this cell to another cell if the other cell is in this cell's links list.
    def link(self, cell, bidirectional = True):        #edge: self->cell
        if bidirectional:
            cell.links.append(self)        #create an edge between the other cell -> this cell
        self.links.append(cell)            # Creates an edge between this cell -> provided cell.

    ## There is an edge from this cell to another cell if the other cell is in this cell's links list.
    def unlink(self, cell, bidirectional = True):       #edge: self->cell
        if bidirectional:
            cell.links.remove(self)        #remove the edge between the other cell -> this cell
        self.links.remove(cell)            #Removes an edge between this cell -> specified cell.

    def is_linked(self, cell):      #Returns true if the other cell is linked to this one
        return bool(cell in self.links)

    def neighbors(self):
        return list(self.neighbor_cells.values())       #Returns all the neighbors of this cell as a list

    ### Returns the linked neighboring cell that has the shortest distance
    def get_closest_cell(self):
        min_distance = float('inf')
        min_cell = None
        for cell in self.links:
            if cell.distance < min_distance:
                min_distance = cell.distance
                min_cell = cell
        return min_cell

    ## Feel free to tweak this to print something different if you'd like
    def print(self):
        print(f"Cell (x: {self.row}, y:{self.col})")

    def __str__(self):
        return f"Cell (x: {self.row}, y:{self.col}, dist: {self.distance}, content: {self.content})"

    def __repr__(self):
        return f"Cell (x: {self.row}, y:{self.col}, dist: {self.distance}, content: {self.content})"

    def get_image(self):
        tile_ht = 50
        tile_wid = 50
        tile = Image.new("RGBA", (tile_wid, tile_ht), self.background_color)
        with tile as im:
            draw = ImageDraw.Draw(im)
            if not self.get_neighbor(Cell.NORTH):
                draw.line((0, 0, tile_wid, 0), fill=self.border_color, width=self.border_width, joint="curve")
            if not self.get_neighbor(Cell.WEST):
                draw.line((0, 0, 0,im.size[1]), fill=self.border_color, width = self.border_width)
            if not self.get_neighbor(Cell.EAST):
                draw.line((im.size[1], 0, im.size[1],im.size[1]), fill=self.border_color, width = self.border_width,joint="curve")
            if not self.get_neighbor(Cell.SOUTH):
                draw.line((0, im.size[1], im.size[0],im.size[1]), fill=self.border_color, width = self.border_width,joint="curve")

            ## Draw the boundaries
            draw.line((0, 0, 0, im.size[1]), fill=self.border_color, width=self.border_width)
            draw.line((0, im.size[1], im.size[0], im.size[1]), fill=self.border_color, width=self.border_width)

            ## Erase them if we're linked
            half_border = self.border_width / 2
            for link in self.links:
                if link == self.get_neighbor(Cell.WEST):
                    draw.line((0, 0+half_border, 0, im.size[1]-half_border), fill=self.background_color, width=self.border_width)
                if link == self.get_neighbor(Cell.SOUTH):
                    draw.line((0+half_border, im.size[1], im.size[0]-half_border,im.size[1]), fill=self.background_color, width = self.border_width)

            ## Draw the content
            font = ImageFont.truetype("AppleGothic.ttf", 20)
            draw.text((im.size[0] / 2, im.size[1] / 2), str(self.content),fill=self.text_color, font = font, anchor="mm")
            #draw.text((im.size[0]/2, im.size[1]/2), str(self.content), fill="black", anchor="mm")

        ## This chunk of code will save an image of just this cell
        ## Feel free to uncomment to help with debugging if needed
        # try:
        #     tile.save(f"images/cell{self.row}-{self.col}.png")
        # except OSError:
        #     print("cannot convert", "Couldn't save the file")
        return tile

class BinaryTreeMazeMaker():

    def __init__(self, grid):
        ## For each cell in the grid
        for index, cell in enumerate(grid):
            ## Set the neighbors to an empty list
            neighbors = []

            ## If the current cell has a neighbor to the south or east, add it to the neighbors list
            if cell.get_neighbor(Cell.SOUTH):
                neighbors.append(cell.get_neighbor(Cell.SOUTH))
            if cell.get_neighbor(Cell.EAST):
                neighbors.append(cell.get_neighbor(Cell.EAST))

            if len(neighbors) > 0:
                ## Choose a random neighbor
                neighbor = random.choice(neighbors)
                ## Link them together
                cell.link(neighbor)


class SidewinderMazeMaker():

    def __init__(self, grid):
        self.grid = grid

        linked_cell = []    #cell for keeping track of the "sidewinder"
        for cur_row in self.grid.rows:
            for cell in cur_row:
                if cell.row == self.grid.num_rows -1 and cell.col == self.grid.num_cols -1: #last element
                    continue
                if cell.row == self.grid.num_rows -1:    #last row: if last row,remove the east wall
                    self.erase_east(cell)
                    continue
                coin = random.choice([0,1])
                if coin == 0:       #erase the east wall
                    if cell.get_neighbor(cell.EAST) == None:    #no eastern neighbor, just delete the south wall
                        #print("erase_south")
                        self.erase_south(cell)# no east neighbor, erase the south wall
                        linked_cell = []    #reset for new row
                        continue
                    linked_cell.append(cell)
                    #print("erase_east")
                    self.erase_east(cell)
                if coin == 1:       #erase the south wall
                    linked_cell.append(cell)
                    chosen_cell = random.choice(linked_cell)
                    #print("erase_south")
                    self.erase_south(chosen_cell)
                    linked_cell = []    #reset list

    def erase_east(self, cell1: Cell):        #   Erase the east wall
        east_neighbor = cell1.get_neighbor(cell1.EAST)
        cell1.link(east_neighbor)

    def erase_south(self, cell1: Cell):        #   Erase the south wall
        south_neighbor = cell1.get_neighbor(cell1.SOUTH)
        cell1.link(south_neighbor)


class DjikstraSolver():

    def __init__(self, grid):
        self.grid = grid

    def solve(self):
        self.initialize()   # Initialize source distances
        source_node = self.grid.get_cell(0,0)
        source_node.distance = 0 # Set the distance to the source node to be 0
        source_node.visited = 1
        heap = []
        heapq.heappush(heap,(source_node.distance,source_node.row,source_node.col,source_node))
        while heap: # While there are more nodes in the heap
            dist, row, col, cell = heapq.heappop(heap)  #node with the smallest distance
            cell.visited = 1
            self.relax(cell)    #relax all the neighbors of that node
            for link_cell in cell.links:
                if not link_cell.visited:
                    #print(link_cell.distance,link_cell.row,link_cell.col)
                    heapq.heappush(heap,(link_cell.distance, link_cell.row, link_cell.col, link_cell))
        return self.recover_path()  # Return the recovered path

    ## Set the distance for all the cells to be "Infinity" (or, 10000 for this assignment)
    def initialize(self):
        for cell in self.grid:
            cell.distance = 10000

    ## The weight function to determine the weight of the edge between 2 nodes
    def weight(self, cell1: Cell, cell2: Cell):
        ## Return the weight of the edge between cell1 and cell2
        if cell1.is_linked(cell2):
            return 1        #connected
        else:
            return 10000    #not connected

    ## Updates the weights; see Relax() in the Djikstra Algorithm slides
    def relax(self, cell1: Cell):
        if cell1 == None:       # If cell is None, do nothing/return
            return
        ## For each neighbor
        for neighbor in cell1.neighbor_cells:
            neighbor_cell = cell1.get_neighbor(neighbor)
            if neighbor_cell.distance > (cell1.distance + self.weight(cell1, neighbor_cell)):
                neighbor_cell.distance = cell1.distance + self.weight(cell1, neighbor_cell)
            ## New distance between is the distance to cell1 plus the distance between cell1 and cell2
            ## if the new distance is less than the distance to cell2:
                ## Set the distance to cell2 to be newDistance

    ## Find the actual path from the source to the target
    ##   utilizing the distances calculated by Djikstra's.
    ## Return a list with the series of nodes that make the shortest path from the source to the target.
    def recover_path(self):
        ## There are many ways to do this; Here's an outline for one approach.
        ##   Feel free to ignore and come up with your own if you'd like!
        source_node = self.grid.get_cell(0,0)    # Get the source node
        target_node = self.grid.get_cell(self.grid.num_rows-1,self.grid.num_cols-1)
        cur_node = target_node
        output = [target_node]      # Put the target in the output list
        while (cur_node != source_node):
            #If we ever can't find a neighbor (shouldn't happen), return an empty list
            if cur_node.get_closest_cell() == None: #changed to couldn't find linked neighbor
                return []
            output.insert(0, cur_node.get_closest_cell())    #find the neighboring cell with the shortest distance assigned to it, add it to the output list
            #print(cur_node.row, cur_node.col)
            cur_node = cur_node.get_closest_cell()
        return output



