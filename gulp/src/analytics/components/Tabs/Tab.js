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
    const {dispatch} = this.props;
    dispatch(doSwitchActiveTab(id));
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
          <a className="filter-switch" href="#" onClick={this.activeTab.bind(this, child.props.id)}>
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
  active: React.PropTypes.bool,
};

export default connect()(Tab);
