import vtk

reader = vtk.vtkRectilinearGridReader()
reader.SetFileName("../data/jet4_0.500.vtk")
reader.Update()
output = reader.GetOutput()

xmi, xma, ymi, yma, zmi, zma = output.GetBounds()

# Color Transfer Function and LookUpTable
# Create transfer mapping scalar value to color
#opacityTransferFunction = vtk.vtkPiecewiseFunction()
opacityTransferFunction = vtk.vtkPiecewiseFunction()
opacityTransferFunction.AddPoint(0, 1.0)
opacityTransferFunction.AddPoint(0.6, 1.0)
opacityTransferFunction.AddPoint(1.3, 1.0)

# Create transfer mapping scalar value to color

colorTransferFunction = vtk.vtkColorTransferFunction()
colorTransferFunction.AddRGBPoint(0, 0.0, 0.0, 1.0)
colorTransferFunction.AddRGBPoint(0.6, 0.0, 1.0, 0.0)
colorTransferFunction.AddRGBPoint(1.3, 1.0, 0.0, 0.0 )

# The property describes how the data will look
volumeProperty = vtk.vtkVolumeProperty()
volumeProperty.SetColor(colorTransferFunction)
volumeProperty.SetScalarOpacity(opacityTransferFunction)
volumeProperty.ShadeOff()
volumeProperty.SetInterpolationTypeToLinear()

tableSize = 30
#
lut = vtk.vtkLookupTable()
lut.SetNumberOfTableValues(tableSize)
lut.Build()
#
for i in range(0,tableSize):
    rgb = list(colorTransferFunction.GetColor(float(i)/tableSize))+[0.5]
    lut.SetTableValue(i,rgb)
        

# A plane for the seeds
plane = vtk.vtkPlaneSource()
plane.SetOrigin(0, 0, 0)
plane.SetPoint1(xma, 0, 0)
plane.SetPoint2(0, 0, zma)
plane.SetXResolution(20)
plane.SetYResolution(20)

# Add the outline of the plane
outline = vtk.vtkOutlineFilter()
outline.SetInputData(plane.GetOutput())
outlineMapper = vtk.vtkPolyDataMapper()
outlineMapper.SetInputConnection(outline.GetOutputPort())
outlineActor = vtk.vtkActor()
outlineActor.SetMapper(outlineMapper)
outlineActor.GetProperty().SetColor(1,1,1)

# Compute streamlines
streamline = vtk.vtkStreamTracer()
streamline.SetSourceConnection(plane.GetOutputPort())
streamline.SetInputConnection(reader.GetOutputPort())
# Try different integration alternatives! See the documentation of vtkStreamTracer
streamline.SetIntegrationDirectionToForward()
streamline.SetMaximumPropagation(1)
streamline.SetComputeVorticity(True)

# Pass the streamlines to the mapper
streamlineMapper = vtk.vtkPolyDataMapper()
streamlineMapper.SetLookupTable(lut)
streamlineMapper.SetInputConnection(streamline.GetOutputPort())
streamlineMapper.SetScalarVisibility(True)
streamlineMapper.SetScalarModeToUsePointFieldData()
streamlineMapper.SelectColorArray('vectors')
# See documentation for the parameter in GetRange()
# http://www.vtk.org/doc/nightly/html/classvtkDataArray.html#ab7efccf59d099c038a4ae269a490e1a3
streamlineMapper.SetScalarRange((reader.GetOutput().GetPointData().GetVectors().GetRange()))

# Pass the mapper to the actor
streamlineActor = vtk.vtkActor()
streamlineActor.SetMapper(streamlineMapper)
streamlineActor.GetProperty().SetLineWidth(2.0)

# Add the outline of the data set
#
#
#
#
#

# Rendering / Window
renderer = vtk.vtkRenderer()
renderer.SetBackground(0.0, 0.0, 0.0)
renderer.AddActor(streamlineActor)
renderer.AddActor(outlineActor)
#renderer.AddActor(gOutlineActor)

renderWindow = vtk.vtkRenderWindow()
renderWindow.AddRenderer(renderer)
renderWindow.SetSize(500, 500)
renderWindow.Render()

interactor = vtk.vtkRenderWindowInteractor()
interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
interactor.SetRenderWindow(renderWindow)
interactor.Initialize()
interactor.Start()
