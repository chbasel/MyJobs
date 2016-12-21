import React from 'react';
import {Component} from 'react';
import d3 from 'd3';
import Paths from '../Common/Paths';
import ToolTip from '../Common/ToolTip';
import mapData from 'common/resources/maps/countries';

class WorldMap extends Component {
  constructor() {
    super();
    this.state = {
      x: 0,
      y: 0,
      country: {},
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
    const {chartData, width, height, margin} = this.props;
    const transform = 'translate(' + margin.left + ',' + margin.top + ')';
    const projection = d3.geo.mercator().translate([width / 2, height / 2]).scale(155);
    const path = d3.geo.path().projection(projection);
    const fill = (countryData) => {
      const rowData = chartData.PageLoadData.rows;
      for (let i = 0; i < rowData.length; i++) {
        if (rowData[i].country === countryData.id) {
          return '#5A6D81';
        }
      }
      return '#E6E6E6';
    };
    const paths = mapData.features.map((country, i) => {
      return (
        <Paths showToolTip={this.showToolTip.bind(this, country)} hideToolTip={this.hideToolTip.bind(this)} key={i} d={path(country)} class="country" stroke="#5A6D81" fill={fill(country)}/>
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
         <g transform={transform}>
           {paths}
         </g>
         </svg>
         <ToolTip activeToolTip={this.state.showToolTip} data={this.state.country} x={this.state.x} y={this.state.y}/>
      </div>
    );
  }
}

WorldMap.propTypes = {
  chartData: React.PropTypes.object.isRequired,
  height: React.PropTypes.number.isRequired,
  width: React.PropTypes.number.isRequired,
  margin: React.PropTypes.object.isRequired,
};

WorldMap.defaultProps = {
  height: 1200,
  width: 1920,
  margin: {top: 50, left: 25, right: 25, bottom: 25},
};

export default WorldMap;
