import numpy as np

def fix(s, es):
    for e in es:
        s = s.constrain(e, "Fixed", None)
    return s

def npoint(p):
    """
    Convert a tuple (x, y) into homogeneous coordinates [x, y, 1].
    """
    x, y = p
    return np.array([x, y, 1])

def point_tuple(p):
    """
    Convert a homogeneous coordinate [x, y, w] back to a tuple (x, y).
    """
    return (p[0] / p[2], p[1] / p[2])

def move(p,d):
    x,y = p
    dx,dy = d
    return (x+dx, y+dy)

def line_from_points(p1, p2):
    """
    Compute the line representation l = [a, b, c] given two points p1 and p2.
    """
    # Cross product to get line equation coefficients
    return np.cross(npoint(p1), npoint(p2))

def intersection_of_lines(l1, l2):
    """
    Compute the intersection point of two lines l1 and l2.
    """
    # Cross product to get intersection point
    p = np.cross(l1, l2)
    
    # Normalize if the third coordinate is not 1 (to keep it in homogeneous coordinates)
    if p[2] != 0:
        p = p / p[2]
    
    return point_tuple(p)

def vertical_line(x1):
    """
    Create a vertical line x = x1 in homogeneous representation [1, 0, -x1].
    """
    return np.array([1, 0, -x1])

def horizontal_line(y1):
    """
    Create a horizontal line y = y1 in homogeneous representation [0, 1, -y1].
    """
    return np.array([0, 1, -y1])

# p1 = npoint((1,1))
# p2 = npoint((3,2))

# l1 = line_from_points(p1, p2)
# print(l1)

# print(np.dot(l1, p1)) # should be close to 0
# print(np.dot(l1, p2)) # should be close to 0

# p3 = intersection_of_lines(l1, vertical_line(2))
# print(point_tuple(p3)) # should be (2,1.5)
