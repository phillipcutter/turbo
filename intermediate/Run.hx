class Run {
	static function main() {
		trace("starting");
		var lst__0__turbo_var__:Dynamic = [];
		for (i in 0...1000000) {
			var abc__1__turbo_var__:Dynamic = 123;
			trace(abc__1__turbo_var__);
			var out__2__turbo_var__:Dynamic;
			if (i % 5 == 0 && i % 3 == 0) {
				out__2__turbo_var__ = "fizzbuzz";
			}
			else if (i % 5 == 0) {
				out__2__turbo_var__ = "fizz";
			}
			else if (i % 3 == 0) {
				out__2__turbo_var__ = "buzz";
			}
			else {
				out__2__turbo_var__ = i;
			}
			lst__0__turbo_var__.push(out__2__turbo_var__);
			trace(out__2__turbo_var__);
		}
		var abc__3__turbo_var__:Dynamic = 345;
		trace(abc__3__turbo_var__);
		trace("ended");
	}
}