import GPOF.display as gd
import GPOF.runset as rs

runset=rs.open_runset(sys.argv[1])

gd.display_2d_points(runset.view(('param1', 'result1')))

gd.display_2d_heatmap(runset.view(('param1', 'param2', 'result2')))
