import React from 'react';
import {Component} from 'react';
import d3 from 'd3';
import Paths from '../Common/Paths';
import ToolTip from '../Common/ToolTip';
import Legend from '../Common/Legend';
import mapData from 'common/resources/maps/us';

class USAMap extends Component {
  constructor() {
    super();
    this.state = {
      x: 0,
      y: 0,
      states: {
        geometry: {},
        properties: {
          STUSPS: '',
          name: '',
        },
        type: '',
      },
      showToolTip: false,
    };
  }
  showToolTip(state, event) {
    this.setState({
      x: event.pageX,
      y: event.pageY,
      states: state,
      showToolTip: true,
    });
  }
  hideToolTip() {
    this.setState({
      showToolTip: false,
    });
  }
  render() {
    const {chartData, width, height, colorRange} = this.props;
    const projection = d3.geo.albersUsa().scale(width).translate([width / 2, height / 2]);
    const path = d3.geo.path().projection(projection);
    const rowData = chartData.PageLoadData.rows;
    const colors = d3.scale.quantize().range(colorRange).domain([1, d3.max(rowData, (d) => d.job_views)]);
    const fill = (stateData) => {
      for (let i = 0; i < rowData.length; i++) {
        if (rowData[i].state === stateData.properties.STUSPS) {
          return colors(rowData[i].job_views);
        }
      }
      return '#E6E6E6';
    };
    const toolTipData = [];
    for (let i = 0; i < rowData.length; i++) {
      const getValues = Object.values(rowData[i]);
      if (getValues[1] === this.state.states.properties.STUSPS) {
        toolTipData.push({...rowData[i]});
      }
    }
    const paths = mapData.features.map((state, i) => {
      return (
        <Paths showToolTip={this.showToolTip.bind(this, state)} hideToolTip={this.hideToolTip.bind(this)} key={i} d={path(state)} class="state" stroke="#5A6D81" fill={fill(state)}/>
      );
    });
    return (
      <div className="chart-container" style={{width: '100%'}}>
        <Legend mapProps={this.props} format=".0f" colorRanges={colors}/>
        <svg
          className="chart"
          height={height}
          width={width}
         >
         {paths}
         <ToolTip activeToolTip={this.state.showToolTip} data={toolTipData} name={this.state.states} x={this.state.x} y={this.state.y} xPosition={495} yPosition={235}/>
         </svg>
      </div>
    );
  }
}

USAMap.propTypes = {
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
  margin: React.PropTypes.object,
  /**
   * Range of colors supplied to the map in the form of an array of rgba values
   */
  colorRange: React.PropTypes.array.isRequired,
};

USAMap.defaultProps = {
  height: 500,
  width: 1920,
  margin: {top: 50, left: 25, right: 25, bottom: 25},
};

export default USAMap;
