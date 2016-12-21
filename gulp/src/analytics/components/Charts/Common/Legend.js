import React from 'react';
import {Component} from 'react';
import d3 from 'd3';

class Legend extends Component {
  render() {
    const {mapProps} = this.props;
    console.log(mapProps);
    const legendData = mapProps.chartData.PageLoadData.rows;
    const legendRectSize = 20;
    const legendSpacing = 40;
    const transform = 'translate(' + (mapProps.width - 400) + ',' + (mapProps.height - 500) + ')';
    const stroke = '#000000';

  //   var color_domain = [50, 150, 350, 750, 1500]
  // var ext_color_domain = [0, 50, 150, 350, 750, 1500]
  // var legend_labels = ["< 50", "50+", "150+", "350+", "750+", "> 1500"]
  // var color = d3.scale.threshold()
  // .domain(color_domain)
  // .range(["#adfcad", "#ffcb40", "#ffba00", "#ff7d73", "#ff4e40", "#ff1300"]);


    const color = d3.scale.linear().domain([0, d3.max(legendData, function(d) {return d.job_views;})]).range(['rgb(222,235,247)', 'rgb(90,109,129)', 'rgb(49,130,189)']);
    const rectData = legendData.map((rect, i) => {
      return (
        <g key={i} transform={`translate(${legendRectSize}, ${(legendSpacing * i) + 50})`}>
          <rect width={legendRectSize + 20} height={legendRectSize + 20} fill={color(rect.job_views)} stroke={stroke}></rect>
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
