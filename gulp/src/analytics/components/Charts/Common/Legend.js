import React from 'react';
import {Component} from 'react';
import d3 from 'd3';

class Legend extends Component {
  render() {
    const {mapProps, format} = this.props;
    const formats = d3.format(format);
    const colors = d3.scale.quantize().range(['rgb(254,229,217)', 'rgb(222,45,38)', 'rgb(165,15,21)']);
    const legendSquares = colors.range().map((color, i) => {
      const r = colors.invertExtent(color);
      const legendText = formats(r[0]);
      return (
        <li key={i} style={{borderTopColor: color}} className="legend-square">
          <span className="legend-range">{legendText}</span>
        </li>
      );
    });
    return (
      <div className="legend">
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
};

export default Legend;
