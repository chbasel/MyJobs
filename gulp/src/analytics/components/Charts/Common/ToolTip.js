import React from 'react';
import {Component} from 'react';
import {isEmpty} from 'lodash-compat/lang';

class ToolTip extends Component {
  render() {
    const {data, x, y, activeToolTip} = this.props;
    return (
      <div className={activeToolTip ? 'chart-tooltip active-tooltip' : 'chart-tooltip'} style={{left: x - 240 + 'px', top: y - 300 + 'px'}}>
        <p className="tool-tip-text">{isEmpty(data) ? '' : data.properties.name}</p>
      </div>
    );
  }
}

ToolTip.propTypes = {
  data: React.PropTypes.object.isRequired,
  x: React.PropTypes.number.isRequired,
  y: React.PropTypes.number.isRequired,
  activeToolTip: React.PropTypes.bool.isRequired,
};

export default ToolTip;
