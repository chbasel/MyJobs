import React from 'react';
import {Component} from 'react';
import d3 from 'd3';

class Legend extends Component {
  render() {
    const {format, colorRanges} = this.props;
    const formats = d3.format(format);
    const legendSquares = colorRanges.range().map((colors, i) => {
      const r = colorRanges.invertExtent(colors);
      const legendText = formats(r[0]) + ' - ' + formats(r[1]);
      return (
        <li key={i} style={{borderTopColor: colors}} className="legend-square">
          <span className="legend-range">{legendText}</span>
        </li>
      );
    });
    return (
      <div className="legend">
        <p>Job Views</p>
        <ul className="legend-list">
          {legendSquares}
        </ul>
      </div>
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
