import React from 'react';
import {Component} from 'react';
import {isEmpty} from 'lodash-compat/lang';

class ToolTip extends Component {
  render() {
    const {data, name, x, y, xPosition, yPosition, activeToolTip} = this.props;
    const dataInfo = data.length > 0 ? data[0].job_views : 0;
    const info = `Job Views: ${dataInfo}`;
    return (
      <div className={activeToolTip ? 'chart-tooltip active-tooltip' : 'chart-tooltip'} style={{left: x - xPosition + 'px', top: y - yPosition + 'px'}}>
        <p className="tool-tip-text tooltip-title">{isEmpty(name) ? '' : name.properties.name}</p>
        <p className="tool-tip-text tooltip-info">{info}</p>
      </div>
    );
  }
}

ToolTip.propTypes = {
  /**
   * Data supplied to the tooltip in the form of an array of objects
   */
  data: React.PropTypes.arrayOf(React.PropTypes.object),
  /**
   * Name of the country or state supplied to the tooltip for the map
   */
  name: React.PropTypes.object.isRequired,
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
