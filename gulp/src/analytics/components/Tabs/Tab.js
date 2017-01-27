import React from 'react';
import {Component} from 'react';
import {connect} from 'react-redux';
import {doSwitchActiveTab} from '../../actions/tab-actions';
import {doRemoveSelectedTab} from '../../actions/tab-actions';

class Tab extends Component {
  constructor(props) {
    super(props);

    this.state = {
      mobileTabs: false,
    };
  }
  activeTab(id, event) {
    event.preventDefault();
    const {dispatch, close} = this.props;
    dispatch(doSwitchActiveTab(id));
    close();
  }
  removeSelectedTab(tabId) {
    const {dispatch} = this.props;
    dispatch(doRemoveSelectedTab(tabId));
  }
  _renderTitles() {
    const {active} = this.props;
    function labels(child, index) {
      const activeTab = (child.props.active ? 'tab active-tab' : 'tab');
      return (
        <li
          key={index}
          className={activeTab}>
          <a className="filter-switch" href="#" title={child.props.label} onClick={this.activeTab.bind(this, child.props.id)}>
            <span className="filter-label">{child.props.label}</span>
          </a>
          <span onClick={this.removeSelectedTab.bind(this, child.props.id)} className="close-tab">X</span>
        </li>
      );
    }
    return (
      <nav className={active ? 'tab-navigation open' : 'tab-navigation'}>
        <ul className="tab-labels">
          {this.props.children.map(labels.bind(this))}
        </ul>
      </nav>
    );
  }
  _renderContent() {
    return (
      <div className="tab-content-container">
        {this.props.children}
      </div>
    );
  }
  render() {
    return (
      <div className="tabs-section">
        {this._renderTitles()}
        {this._renderContent()}
      </div>
    );
  }
}


Tab.propTypes = {
  children: React.PropTypes.arrayOf(
    React.PropTypes.element.isRequired,
  ),
  dispatch: React.PropTypes.func.isRequired,
  /**
   * Active boolean to display which tab information is active on the screen
   */
  active: React.PropTypes.bool,
  /**
   * Function to close a tab using the X button in the top right corner of the tab
   */
  close: React.PropTypes.func,
};

export default connect()(Tab);
