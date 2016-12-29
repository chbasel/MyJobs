import React from 'react';
import {Component} from 'react';
import {isEmpty} from 'lodash-compat/lang';

class ToolTip extends Component {
  render() {
    const {data, x, y, xPosition, yPosition, activeToolTip} = this.props;
    return (
      <div className={activeToolTip ? 'chart-tooltip active-tooltip' : 'chart-tooltip'} style={{left: x - xPosition + 'px', top: y - yPosition + 'px'}}>
        <p className="tool-tip-text">{isEmpty(data) ? '' : data.properties.name}</p>
      </div>
    );
  }
}

ToolTip.propTypes = {
  /**
   * Data supplied to the tooltip
   */
  data: React.PropTypes.object.isRequired,
  /**
   * x coordinate of the tooltip
   */
  x: React.PropTypes.number.isRequired,
  /**
   * x position of the tooltip
   */
  xPosition: React.PropTypes.number.isRequired,
  /**
   * y coordinate of the tooltip
   */
  y: React.PropTypes.number.isRequired,
  /**
   * y position of the tooltip
   */
  yPosition: React.PropTypes.number.isRequired,
  /**
   * true or false on whether or not to display the tooltip typically on hover
   */
  activeToolTip: React.PropTypes.bool.isRequired,
};

export default ToolTip;
