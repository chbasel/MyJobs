import React from 'react';
import {Component} from 'react';
import d3 from 'd3';
import Paths from '../Common/Paths';
import ToolTip from '../Common/ToolTip';
// import Legend from '../Common/Legend';
import mapData from 'common/resources/maps/us';

class USAMap extends Component {
  constructor() {
    super();
    this.state = {
      x: 0,
      y: 0,
      state: {},
      showToolTip: false,
    };
  }
  showToolTip(state, event) {
    this.setState({
      x: event.pageX,
      y: event.pageY,
      state: state,
      showToolTip: true,
    });
  }
  hideToolTip() {
    this.setState({
      showToolTip: false,
    });
  }
  render() {
    const {chartData, width, height, scale, pathClicked} = this.props;
    const projection = d3.geo.albersUsa().scale(scale).translate([width / 2, height / 2]);
    const path = d3.geo.path().projection(projection);
    const fill = (stateData) => {
      const rowData = chartData.PageLoadData.rows;
      const color = d3.scale.linear().domain([0, d3.max(rowData, (d) => d.job_views)]).range(['rgb(222,235,247)', 'rgb(90,109,129)', 'rgb(49,130,189)']);
      for (let i = 0; i < rowData.length; i++) {
        if (rowData[i].state === stateData.properties.STUSPS) {
          return color(rowData[i].job_views);
        }
      }
      return '#E6E6E6';
    };
    const stateClicked = (state) => {
      return () => {pathClicked(state.properties.STUSPS, "state")};
    };
    const paths = mapData.features.map((state, i) => {
      return (
        <Paths onClick={stateClicked(state)} showToolTip={this.showToolTip.bind(this, state)} hideToolTip={this.hideToolTip.bind(this)} key={i} d={path(state)} class="state" stroke="#5A6D81" fill={fill(state)}/>
      );
    });
    return (
      <div className="chart-container" style={{width: '100%'}}>
        <svg
          className="chart"
          version="1.1"
          height={height}
          width={width}
          viewBox={'0 0 ' + width + ' ' + height + ''}
          preserveAspectRatio="xMinYMin meet"
         >
         {paths}
         </svg>
         <ToolTip activeToolTip={this.state.showToolTip} data={this.state.state} x={this.state.x} y={this.state.y}/>
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
   * Scale is a type of number for the scale of the map in terms of how zoomed in or out the display is
   */
  scale: React.PropTypes.number.isRequired,
  /**
   * pathClicked is a function to be called when a path on the chart is clicked
   */
  pathClicked: React.PropTypes.func
};

USAMap.defaultProps = {
  height: 500,
  width: 1920,
  scale: 1000,
  margin: {top: 50, left: 25, right: 25, bottom: 25},
  pathClicked: () => {},
};

export default USAMap;
