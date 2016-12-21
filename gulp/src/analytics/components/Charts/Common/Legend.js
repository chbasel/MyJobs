import React from 'react';
import {Component} from 'react';

class Legend extends Component {
  render() {
    const {mapProps} = this.props;
    const legendSize = 200;
    const transform = 'translate(' + (mapProps.width - 300) + ',' + 100 + ')';
    const stroke = '#000000';
    const fill = '#FFFFFF';
    const textX = 4;
    const textY = legendSize * 2;
    return (
      <g className="map-legend" transform={transform}>
        <rect
          width={legendSize}
          height={legendSize}
          fill={fill}
          stroke={stroke}
          x="50"
          y="50"
        >
        </rect>
        <rect
          width={legendSize}
          height={legendSize}
          fill={fill}
          stroke={stroke}
        >
        </rect>
      </g>
    );
  }
}

Legend.propTypes = {
  mapProps: React.PropTypes.object.isRequired,
};

export default Legend;
