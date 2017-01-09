import React from 'react';
import {Component} from 'react';

class Paths extends Component {
  render() {
    const {d, fill, stroke, classes, showToolTip, hideToolTip, onClick} = this.props;
    return (
      <path onClick={onClick} onMouseEnter={showToolTip} onMouseLeave={hideToolTip} d={d} fill={fill} stroke={stroke} className={classes}></path>
    );
  }
}

Paths.propTypes = {
  d: React.PropTypes.string,
  fill: React.PropTypes.string,
  stroke: React.PropTypes.string,
  classes: React.PropTypes.string,
  showToolTip: React.PropTypes.func,
  hideToolTip: React.PropTypes.func,
  onClick: React.PropTypes.func,
};

export default Paths;
