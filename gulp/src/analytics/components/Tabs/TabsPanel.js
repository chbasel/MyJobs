import React from 'react';
import {Component} from 'react';

class TabsPanel extends Component {
  render() {
    const {active} = this.props;
    return (
      <div className={active ? 'tab-panel active-panel' : 'tab-panel'}>
        {this.props.children}
      </div>
    );
  }
}

TabsPanel.propTypes = {
  children: React.PropTypes.arrayOf(
    React.PropTypes.element.isRequired,
  ),
  active: React.PropTypes.bool.isRequired,
};

export default TabsPanel;
