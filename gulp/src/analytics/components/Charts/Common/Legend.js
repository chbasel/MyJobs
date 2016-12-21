import React from 'react';
import {Component} from 'react';

class Legend extends Component {
  render() {
    const {mapProps} = this.props;
    console.log(mapProps);
    const legendData = mapProps.chartData.PageLoadData.rows;
    const legendRectSize = 20;
    const legendSpacing = 10;
    const margin = 2;
    const transform = 'translate(' + (mapProps.width - 400) + ',' + (mapProps.height - 300) + ')';
    const stroke = '#000000';
    const fill = '#000000';
    const rectData = legendData.map((rect, i) => {
      return (
        <g key={i} transform={`translate(${legendRectSize}, ${legendRectSize * i++ + 50})`}>
          <rect width={legendRectSize + 20} height={legendRectSize + 20} fill={fill} stroke={stroke} x="50" y="50">
            <text>{rect.country}</text>
          </rect>
        </g>
      );
    });
    // const textX = 4;
    // const textY = legendSize * 2;
    return (
      <g>
        <g className="map-legend" transform={transform}>
          {rectData}
        </g>
      </g>
    );
  }
}

Legend.propTypes = {
  mapProps: React.PropTypes.object.isRequired,
};

export default Legend;
