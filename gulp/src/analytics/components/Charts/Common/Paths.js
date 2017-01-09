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
  /**
   * Data supplied to each path which is specifically some type of longitude or latitude
   */
  d: React.PropTypes.string,
  /**
   * Fill inside color of the given paths
   */
  fill: React.PropTypes.string,
  /**
   * Stroke outline color of the paths
   */
  stroke: React.PropTypes.string,
  /**
   * Classnames that can be applied to the paths
   */
  classes: React.PropTypes.string,
  /**
   * Function for showing the tooltip for a given path
   */
  showToolTip: React.PropTypes.func,
  /**
   * Function for hiding the tooltip for a given path
   */
  hideToolTip: React.PropTypes.func,
  onClick: React.PropTypes.func,
};

export default Paths;
