import React from 'react';
import {Component} from 'react';
import {connect} from 'react-redux';
import {Button} from 'react-bootstrap';
import Calendar from '../Calendar/Calendar';

class Header extends Component {
  constructor(props) {
    super(props);

    this.state = {
      showPicker: false,
    };
  }
  /**
   * Handling the click event outside of the Calendar to close the calendar
   */
  componentDidMount() {
    window.addEventListener('mousedown', this.pageClick.bind(this), false);
  }
  pageClick() {
    if (this.mouseIsDownOnCalendar) {
      return;
    }
    this.setState({
      showPicker: false,
    });
  }
  mouseDownHandler() {
    this.mouseIsDownOnCalendar = true;
  }
  mouseUpHandler() {
    this.mouseIsDownOnCalendar = false;
  }
  showCalendarRangePicker() {
    this.setState({
      showPicker: true,
    });
  }
  hideCalendarRangePicker() {
    this.setState({
      showPicker: false,
    });
  }
  render() {
    const {analytics, toggleTabs, tabsActive} = this.props;
    return (
      <div className="tabs-header">
        <nav id="tab_header_navigation">
          <i onClick={toggleTabs} className={tabsActive ? 'arrow-active fa fa-arrow-circle-right open-mobile-tabs' : 'fa fa-arrow-circle-right open-mobile-tabs'} aria-hidden="true"></i>
          <i onClick={toggleTabs} className={tabsActive ? 'fa fa-arrow-circle-left close-mobile-tabs' : 'arrow-active fa fa-arrow-circle-left close-mobile-tabs'} aria-hidden="true"></i>
          <ul className="nav navbar-nav navbar-right right-options">
            <li>
              <Button onClick={this.showCalendarRangePicker.bind(this)} className="selected-date-range-btn">
                  <i className="head-icon fa fa-calendar" aria-hidden="true"></i>
                  <span className="dashboard-date">{analytics.stateCustomRange}</span>
              </Button>
            </li>
          </ul>
        </nav>
        <Calendar onMouseDown={this.mouseDownHandler.bind(this)} onMouseUp={this.mouseUpHandler.bind(this)} showCalendarRangePicker={this.state.showPicker} hideCalendarRangePicker={this.hideCalendarRangePicker.bind(this)}/>
      </div>
    );
  }
}

Header.propTypes = {
  dispatch: React.PropTypes.func.isRequired,
  analytics: React.PropTypes.object.isRequired,
  /**
   * Toggling the tabs being active or non active for the arrows in mobile view
   */
  toggleTabs: React.PropTypes.func.isRequired,
  /**
   * Boolean stating whether or not the tabs are actively displayed in mobile view
   */
  tabsActive: React.PropTypes.bool.isRequired,
};

export default connect(state => ({
  analytics: state.pageLoadData,
}))(Header);
