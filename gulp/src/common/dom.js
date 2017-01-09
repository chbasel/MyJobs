import {SpringSystem} from 'rebound';

/* scrollUp(increment : Number, position: Number) => null
 * Given an increment and a position, repeatedly scrolls the viewport upward
 * `increment` pixels until the viewport is at `position`.
 */
export const scrollUp = (increment = 250, position = 0) => {
  // Chrome recognizes document.body, but Firefox recognizes
  // document.documentElement. Both return 0 on each browser, which is why I
  // can't simply define an alias to use for both.
  let scrollTop = document.documentElement.scrollTop ||
                  document.body.scrollTop;
  const scrollInterval = ((0 - scrollTop) / increment) * 10;

  const scrollLoop = setInterval(() => {
    if (scrollTop <= position) {
      clearInterval(scrollLoop);
    }

    document.documentElement.scrollTop += scrollInterval;
    document.body.scrollTop += scrollInterval;
    scrollTop = document.documentElement.scrollTop || document.body.scrollTop;
  }, 10);
};

/* isIE8
 * Returns true if the current browser is IE 8 or false otherwise. Works off of
 * the assumption that the addEventListener DOM method isn't available on IE 8.
 */
export const isIE8 = !Boolean(window.addEventListener);

/**
 * Utility for scrolling smoothly.
 *
 *  update: a function which is called frequenly with new scroll values
 *    when scrolling.
 *
 *  const scroller = new SmoothScroller(h => {container.scrollTop = h;});
 *
 *  scroller.springToShow(someItem, container); // Smoothly scrolls.
 */
export class SmoothScroller {
  constructor(update) {
    this.system = new SpringSystem();
    this.spring = this.system.createSpring(87, 8);
    this.spring.setOvershootClampingEnabled(true);
    this.update = update;
    this.spring.addListener({
      onSpringUpdate: spring => this.update(spring.getCurrentValue()),
    });
    this.system.loop();
  }

  /**
   * Clean up resources associated with this object.
   */
  destroy() {
    this.spring.destroy();
  }

  /**
   * Call update function to scroll to a specific location.
   */
  springTo(value) {
    this.spring.setEndValue(value);
  }

  /**
   * Move spring position directly without updating.
   */
  skipTo(value) {
    this.spring.setCurrentValue(value);
  }

  /**
   * Call update function to make ref visible in containerRef.
   *
   * ref: item which needs to be seen
   * containerRef: scrollable container.
   */
  springToShow(ref, containerRef) {
    if (ref.offsetTop < containerRef.scrollTop) {
      this.springTo(ref.offsetTop);
      return;
    }

    if (ref.offsetTop + ref.clientHeight >
        containerRef.scrollTop + containerRef.clientHeight) {
      this.springTo(ref.offsetTop + ref.clientHeight
        - containerRef.clientHeight);
      return;
    }
  }
}

/**
 * Scroll an item vertically so that it is visible within a container.
 *
 * ref: item which needs to be seen
 * containerRef: scrollable container.
 */
export function scrollToVisible(ref, containerRef) {
  if (ref.offsetTop < containerRef.scrollTop) {
    containerRef.scrollTop = ref.offsetTop;
    return;
  }

  if (ref.offsetTop + ref.clientHeight >
      containerRef.scrollTop + containerRef.clientHeight) {
    containerRef.scrollTop = ref.offsetTop + ref.clientHeight -
      containerRef.clientHeight;
    return;
  }
}
