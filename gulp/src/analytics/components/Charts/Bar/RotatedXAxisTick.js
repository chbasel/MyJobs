import React from 'react';
import {Component} from 'react';
import {Text} from 'recharts';

class RotatedXAxisTick extends Component {
  render() {
    function truncate(length, value) {
      if (value.length > length) {
        return value.substring(0, length) + '...';
      }
      return value;
    }

    const {fill, payload, x, y} = this.props;

    return (
      <g transform={`translate(${x},${y})`}>
        <Text
          textAnchor="end"
          verticalAnchor="middle"
          fill={fill}
          angle={-45}
        >
          {truncate(15, payload.value)}
        </Text>
      </g>
    );
  }
}

RotatedXAxisTick.propTypes = {
  fill: React.PropTypes.string,
  payload: React.PropTypes.object,
  x: React.PropTypes.number,
  y: React.PropTypes.number,
};

export default RotatedXAxisTick;
