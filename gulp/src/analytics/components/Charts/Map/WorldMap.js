import React from 'react';
import {Component} from 'react';
import d3 from 'd3';
import Paths from '../Common/Paths';
import ToolTip from '../Common/ToolTip';
import Legend from '../Common/Legend';
import mapData from 'common/resources/maps/countries';

class WorldMap extends Component {
  constructor() {
    super();
    this.state = {
      x: 0,
      y: 0,
      country: {
        geometry: {},
        id: '',
        properties: {},
        type: '',
      },
      showToolTip: false,
    };
  }
  showToolTip(country, event) {
    this.setState({
      x: event.pageX,
      y: event.pageY,
      country: country,
      showToolTip: true,
    });
  }
  hideToolTip() {
    this.setState({
      showToolTip: false,
    });
  }
  render() {
    const {chartData, width, height, margin, scale, pathClicked, colorRange} = this.props;
    const transform = 'translate(' + margin.left + ',' + margin.top + ')';
    const projection = d3.geo.mercator().translate([width / 2, height / 2]).scale(scale);
    const path = d3.geo.path().projection(projection);
    const rowData = chartData.PageLoadData.rows;
    const colors = d3.scale.quantize().range(colorRange).domain([1, d3.max(rowData, (d) => d.job_views)]);
    const fill = (countryData) => {
      for (let i = 0; i < rowData.length; i++) {
        if (rowData[i].country === countryData.id) {
          return colors(rowData[i].job_views);
        }
      }
      return '#E6E6E6';
    };
    const countryClicked = (country) => {
      return () => {pathClicked(country.id, 'country');};
    };
    const toolTipData = [];
    for (let i = 0; i < rowData.length; i++) {
      const getValues = Object.values(rowData[i]);
      if (getValues[0] === this.state.country.id) {
        toolTipData.push({...rowData[i]});
      }
    }
    const paths = mapData.features.map((country, i) => {
      return (
        <Paths onClick={countryClicked(country)} showToolTip={this.showToolTip.bind(this, country)} hideToolTip={this.hideToolTip.bind(this)} key={i} d={path(country)} class="country" stroke="#5A6D81" fill={fill(country)}/>
      );
    });
    return (
      <div className="chart-container" style={{width: '100%'}}>
        <Legend mapProps={this.props} format=".0f" colorRanges={colors}/>
        <svg
          className="chart"
          version="1.1"
          height={height}
          width={width}
          viewBox={'0 0 ' + width + ' ' + height + ''}
          preserveAspectRatio="xMinYMin meet"
         >
         <g transform={transform}>
           {paths}
         </g>
         </svg>
         <ToolTip activeToolTip={this.state.showToolTip} data={toolTipData} name={this.state.country} x={this.state.x} y={this.state.y} xPosition={355} yPosition={275}/>
      </div>
    );
  }
}

WorldMap.propTypes = {
  /**
   * Type of object representing the data going into the object
   */
  chartData: React.PropTypes.object.isRequired,
  /**
   * Type is a number for the height of the chart
   */
  height: React.PropTypes.number.isRequired,
  /**
   * Type is a number value for the width of the map
   */
  width: React.PropTypes.number.isRequired,
  /**
   * Margin is an object with keys of left, right, top, bottom and values equaling numbers for the margins of the map
   */
  margin: React.PropTypes.object.isRequired,
  /**
   * Scale is a type of number for the scale of the map in terms of how zoomed in or out the display is
   */
  scale: React.PropTypes.number.isRequired,
  /**
   * pathClicked is a function to be called when a path on the chart is clicked
   */
  pathClicked: React.PropTypes.func,
   /**
   * Range of colors supplied to the map in the form of an array of rgba values
   */
  colorRange: React.PropTypes.array.isRequired,
};

WorldMap.defaultProps = {
  height: 500,
  width: 1920,
  scale: 100,
  margin: {top: 50, left: 25, right: 25, bottom: 25},
  pathClicked: () => {},
};

export default WorldMap;
