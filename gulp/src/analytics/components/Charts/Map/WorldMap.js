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
    const {chartData, width, height, projectionScale, colorRange} = this.props;
    const projection = d3.geo.mercator().translate([width / 2, height / 1.65]).scale(projectionScale);
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
    const toolTipData = [];
    for (let i = 0; i < rowData.length; i++) {
      const getValues = Object.values(rowData[i]);
      if (getValues[0] === this.state.country.id) {
        toolTipData.push({...rowData[i]});
      }
    }
    const paths = mapData.features.map((country, i) => {
      return (
        <Paths showToolTip={this.showToolTip.bind(this, country)} hideToolTip={this.hideToolTip.bind(this)} key={i} d={path(country)} class="country" stroke="#5A6D81" fill={fill(country)}/>
      );
    });
    console.log('Full width: ', width);
    console.log('Full height: ', height);
    return (
      <div className="chart-container" style={{width: '100%'}}>
        <svg
          className="chart"
          height={height}
          width={width}
         >
           {paths}
           <Legend mapProps={this.props} legendRectX={width * 0.035 * 0.86} legendTextX={width * 0.035 * 2.2} legendTranslateX={(width - 100)} height={(height * 0.04)} width={(width * 0.035)} format=".0f" colorRanges={colors}/>
         </svg>
         <ToolTip activeToolTip={this.state.showToolTip} data={toolTipData} name={this.state.country} x={this.state.x} y={this.state.y} xPosition={240} yPosition={245}/>
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
   * Scale for the projection of the SVG
   */
  projectionScale: React.PropTypes.number,
  /**
   * Scale for the G element transform using X and Y coordinates in form of an object with key value pairs
   */
  transformScale: React.PropTypes.object,
  /**
   * Translate for the G element transform using x and y coordinates in the form of an object with key value pairs
   */
  transformTranslate: React.PropTypes.object,
  /**
   * Range of colors supplied to the map in the form of an array of rgba values
   */
  colorRange: React.PropTypes.array.isRequired,
};

WorldMap.defaultProps = {
  height: 500,
  width: 1920,
  projectionScale: 100,
  transformScale: {x: 1.5, y: 1.3},
  transformTranslate: {x: -25, y: 75},
};

export default WorldMap;
