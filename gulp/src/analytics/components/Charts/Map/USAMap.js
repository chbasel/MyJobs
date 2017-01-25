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
    const {chartData, width, height, colorRange, pathClicked} = this.props;
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
    const stateClicked = (state) => {
      return () => {pathClicked(state.properties.STUSPS, 'state');};
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
        <Paths onClick={stateClicked(state)} showToolTip={this.showToolTip.bind(this, state)} hideToolTip={this.hideToolTip.bind(this)} key={i} d={path(state)} class="state" stroke="#5A6D81" fill={fill(state)}/>
      );
    });
    return (
      <div className="chart-container" style={{width: '100%'}}>
        <svg
          className="chart"
          height={height}
          width={width}
         >
         {paths}
         <Legend mapProps={this.props} legendTitleX={width * 0.035 * 1.33} legendTitleY={height * 0.04 * (-1.5)} borderTransform={`translate(0, ${height * -0.024})`} legendTransform={`translate(${(width - 100) * 1.14}, ${width * 0.035 * 3})`} legendRectX={width * 0.035 * 0.86} legendTextX={width * 0.035 * 2.2} height={(height * 0.04)} width={(width * 0.035)} format=".0f" colorRanges={colors}/>
         </svg>
         <ToolTip activeToolTip={this.state.showToolTip} data={toolTipData} name={this.state.states} x={this.state.x} y={this.state.y} xPosition={240} yPosition={245}/>
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
   * pathClicked is a function to be called when a path on the chart is clicked
   */
  pathClicked: React.PropTypes.func,
  /**
   * Range of colors supplied to the map in the form of an array of rgba values
   */
  colorRange: React.PropTypes.array.isRequired,
};

USAMap.defaultProps = {
  height: 500,
  width: 1920,
  margin: {top: 50, left: 25, right: 25, bottom: 25},
  pathClicked: () => {},
};

export default USAMap;
