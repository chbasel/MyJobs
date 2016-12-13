import d3 from 'd3';
import React from 'react';
import {Component} from 'react';
import Axis from '../Common/Axis';
import Grid from '../Common/Grid';

class BarChart extends Component {
  render() {
    const {chartData} = this.props;
    const chartingData = chartData.PageLoadData.rows;
    const margin = {top: 20, bottom: 100, left: 80, right: 20};
    const height = this.props.svgHeight - margin.top - margin.bottom;
    const width = this.props.svgWidth - margin.left - margin.right;
    const transform = 'translate(' + margin.left + ',' + margin.top + ')';
    const xScale = d3.scale.ordinal()
    .domain(chartingData.map((d) => {
      return d.found_on;
    }))
    .rangeBands([0, width], 0, 0.2);
    const yScale = d3.scale.linear()
    .domain([0, d3.max(chartingData, (d) => {
      return d.job_views;
    })])
    .range([height, 0]);
    const xAxis = d3.svg.axis()
    .scale(xScale)
    .orient('bottom');
    const yAxis = d3.svg.axis()
    .scale(yScale)
    .ticks(8)
    .orient('left');
    const yGrid = d3.svg.axis()
    .scale(yScale)
    .orient('left')
    .ticks(8)
    .tickSize(-width, 10, 0)
    .tickPadding(10)
    .tickFormat('');
    const rectHeight = (d) => {
      return height - yScale(d.job_views);
    };
    const rectWidth = () => {
      return xScale.rangeBand() - 50;
    };
    const x = (d) => {
      return xScale(d.found_on);
    };
    const y = (d) => {
      return yScale(d.job_views);
    };
    const rect = (chartingData).map((d, i) => {
      return (
        <rect
          fill="#5a6d81"
          x={x(d, i)}
          y={y(d, i)}
          key={i}
          height={rectHeight(d)}
          width={rectWidth(d)}
        />
    );
    });

    return (
      <div className="chart-container" style={{width: '100%'}}>
        <svg
          className="chart"
          height={this.props.svgHeight}
          width={this.props.svgWidth}
          version="1.1"
          style={{width: '100%', minWidth: '250px', height: 'auto'}}
          viewBox="0 0 1920 600"
          preserveAspectRatio="xMinYMin meet"
        >
           <g transform={transform}>
             <Grid height={height} grid={yGrid} gridType="y"/>
             <Axis height={height} width={width} axis={xAxis} axisType="x" />
             <Axis height={height} axis={yAxis} axisType="y" />
             {rect}
          </g>
        </svg>
      </div>
    );
  }
}

BarChart.propTypes = {
  chartData: React.PropTypes.object.isRequired,
  svgHeight: React.PropTypes.number.isRequired,
  svgWidth: React.PropTypes.number.isRequired,
  svgId: React.PropTypes.string,
};

BarChart.defaultProps = {
  svgHeight: 600,
  svgWidth: 1920,
  svgId: 'bar_svg',
};

export default BarChart;