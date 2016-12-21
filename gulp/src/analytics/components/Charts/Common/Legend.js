import React from 'react';
import {Component} from 'react';
import d3 from 'd3';

class Legend extends Component {
  render() {
    const {mapProps} = this.props;
    const legendData = mapProps.chartData.PageLoadData.rows;
    const legendRectSize = 20;
    const legendSpacing = 40;
    const transform = 'translate(' + (mapProps.width - 400) + ',' + (mapProps.height - 500) + ')';
    const stroke = '#000000';
    const color = d3.scale.linear().domain([0, d3.max(legendData, (d) => d.job_views)]).range(['rgb(222,235,247)', 'rgb(90,109,129)', 'rgb(49,130,189)']);
    const rectData = legendData.map((rect, i) => {
      return (
        <g key={i} transform={`translate(${legendRectSize}, ${(legendSpacing * i) + 50})`}>
          <rect width={legendRectSize + 20} height={legendRectSize + 20} fill={color} stroke={stroke}></rect>
          <text x="50" y="30">{rect.country}</text>
        </g>
      );
    });
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
