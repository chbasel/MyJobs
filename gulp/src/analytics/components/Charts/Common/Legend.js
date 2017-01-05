import React from 'react';
import {Component} from 'react';
import d3 from 'd3';

class Legend extends Component {
  render() {
    const {format, colorRanges, legendTranslateX, legendTranslateY} = this.props;
    const formats = d3.format(format);
    const legendSquares = colorRanges.range().map((colors, i) => {
      const r = colorRanges.invertExtent(colors);
      const legendText = formats(r[0]) + ' - ' + formats(r[1]);
      return (
        <g key={i}>
          <rect x="20" y={20 * i + (10 * i)} className="legend-squares" width="40" height="10" fill={colors} strokeWidth="1" stroke="#000000" />
          <text x="70" y={20 * i + (10 * i) + (10)} className="legend-range">{legendText}</text>
        </g>
      );
    });
    return (
      <g transform={'translate(' + legendTranslateX + ',' + 200 + ')'}>
        <text>Job Views</text>
        <rect transform={'translate(0, -15)'} fill="#FFFFFF" class="legend-box" strokeWidth="1" stroke="#5A6D81" width="150" height="225"></rect>
        {legendSquares}
      </g>
    );
  }
}

Legend.propTypes = {
  /**
   * Object of the data from the map that gets sent to the legend
   */
  mapProps: React.PropTypes.object.isRequired,
  /**
   * String format for the labels of the legend
   */
  format: React.PropTypes.string.isRequired,
  /**
   * Function passed to the legend in order to populate the colors and values
   */
  colorRanges: React.PropTypes.func.isRequired,
};

export default Legend;
