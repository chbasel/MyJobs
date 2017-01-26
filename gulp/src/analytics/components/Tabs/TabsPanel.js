import React from 'react';
import {Component} from 'react';

class TabsPanel extends Component {
  render() {
    const {active, updatedMessage} = this.props;
    return (
      <div className={active ? 'tab-panel active-panel' : 'tab-panel'}>
        <div id="update_notification" className={updatedMessage ? 'show-update alert alert-success' : 'hide-update alert alert-success'}>
          <strong>Tab data has been updated successfully!</strong>
        </div>
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
  /**
   * Boolean telling whether or not to show the message for the tab data being updated or not
   */
  updatedMessage: React.PropTypes.bool.isRequired,
};

export default TabsPanel;
