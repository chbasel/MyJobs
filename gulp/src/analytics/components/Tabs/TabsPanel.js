import React from 'react';
import {Component} from 'react';

class TabsPanel extends Component {
  render() {
    return (
      <div className="tab-content">
        <div>
          {this.props.children}
        </div>
      </div>
    );
  }
}

TabsPanel.propTypes = {
  children: React.PropTypes.arrayOf(
    React.PropTypes.element.isRequired,
  ),
};

export default TabsPanel;
