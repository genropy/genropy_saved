/**
 * Parameters from protovis.py:
 *
 * vis -- the root Pv.Panel object
 * height -- the height getter function
 * width -- the width getter function
 * data -- the data getter function
 */

vis.width(width).height(height);

vis.add(pv.Rule)
    .data(pv.range(0, 1, 0.5))
    .bottom(function(d) d*80 + 0.5)
    .add(pv.Label);

vis.add(pv.Bar)
    .data(data)
    .width(20)
    .height(function(d) d*80)
    .bottom(0)
    .left(function() this.index * 25 + 25)
    .anchor("bottom").add(pv.Label);
