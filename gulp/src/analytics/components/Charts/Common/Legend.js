import React from 'react';
import {Component} from 'react';
import d3 from 'd3';

class Legend extends Component {
  render() {
    const {format, colorRanges, legendRectX, legendTextX, legendTranslateX, height, width} = this.props;
    const formats = d3.format(format);
    const legendSquares = colorRanges.range().map((colors, i) => {
      const r = colorRanges.invertExtent(colors);
      const legendText = formats(r[0]) + ' - ' + formats(r[1]);
      return (
        <g key={i}>
          <rect x={legendRectX} y={(height * 0.02) * i + ((height * 2) * i)} className="legend-squares" width={width} height={height} fill={colors} strokeWidth="1" stroke="#000000" />
          <text x={legendTextX} y={(height * 0.012) * i + ((height * 2) * i) + (12)} className="legend-range">{legendText}</text>
        </g>
      );
    });
    return (
      <g transform={`translate(${legendTranslateX * 1.1}, ${width * 3})`}>
        <text y={height * (-1.5)} x={width * 1.3}>Job Views</text>
        <rect transform={'translate(0, -15)'} fill="#FFFFFF" className="legend-box" strokeWidth="1" stroke="#5A6D81" width={(width * 5)} height={(height * 15)}></rect>
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
  /**
   * Number passed for translating the X value
   */
  legendTranslateX: React.PropTypes.number.isRequired,
  /**
   * Number representing the height of the parent container for responsiveness
   */
  height: React.PropTypes.number.isRequired,
  /**
   * Number representing the width of the parent container for responsiveness
   */
  width: React.PropTypes.number.isRequired,
  /**
   * Number representing the X coordinates of the rectangles making up the legend
   */
  legendRectX: React.PropTypes.number.isRequired,
  /**
   * Number representing the X coordinates of the text making up the legend
   */
  legendTextX: React.PropTypes.number.isRequired,
};

export default Legend;
