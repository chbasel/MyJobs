import React from 'react';
import {Component} from 'react';
import d3 from 'd3';
import Paths from '../Common/Paths';
import ToolTip from '../Common/ToolTip';
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
    const {chartData, width, height} = this.props;
    const projection = d3.geo.albersUsa().scale(1450).translate([width / 2, height / 2]);
    const path = d3.geo.path().projection(projection);
    const fill = (stateData) => {
      const rowData = chartData.PageLoadData.rows;
      for (let i = 0; i < rowData.length; i++) {
        if (rowData[i].state === stateData.properties.STUSPS) {
          return '#5A6D81';
        }
      }
      return '#E6E6E6';
    };
    const paths = mapData.features.map((state, i) => {
      return (
        <Paths showToolTip={this.showToolTip.bind(this, state)} hideToolTip={this.hideToolTip.bind(this)} key={i} d={path(state)} class="state" stroke="#5A6D81" fill={fill(state)}/>
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
  chartData: React.PropTypes.object.isRequired,
  height: React.PropTypes.number.isRequired,
  width: React.PropTypes.number.isRequired,
};

USAMap.defaultProps = {
  height: 800,
  width: 1920,
  margin: {top: 50, left: 25, right: 25, bottom: 25},
};

export default USAMap;
