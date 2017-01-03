import React from 'react';
import {Component} from 'react';
import {connect} from 'react-redux';
import {doSwitchActiveTab} from '../../actions/tab-actions';
import {doRemoveSelectedTab} from '../../actions/tab-actions';

class Tab extends Component {
  constructor(props) {
    super(props);

    this.toggleTabs = this.toggleTabs.bind(this);

    this.state = {
      mobileTabs: false,
    };
  }
  toggleTabs() {
    this.setState({
      mobileTabs: !this.state.mobileTabs,
    });
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
      <nav className={this.state.mobileTabs ? 'tab-navigation open' : 'tab-navigation'}>
        <div onClick={this.toggleTabs} className={this.state.mobileTabs ? 'mobile-tab open' : 'mobile-tab close'}><span className={this.state.mobileTabs ? 'tabs-closed mobile-tab-label' : 'mobile-tab-label'}>Tabs</span><i className={this.state.mobileTabs ? 'fa fa-times close-mobile-tabs' : 'fa fa-times close-mobile-tabs tabs-closed'} aria-hidden="true"></i></div>
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
  // tabData: React.PropTypes.object.isRequired,
  dispatch: React.PropTypes.func.isRequired,
};

export default connect()(Tab);
