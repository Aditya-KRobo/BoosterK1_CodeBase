#include "example_agent.hpp"
int main(int argc, char *argv[]) {
  rclcpp::init(argc, argv);
  // Agent id must be aligned with value in agent.json
  auto node = std::make_shared<ExampleAgent>("com.boosterobotics.example");
  rclcpp::executors::MultiThreadedExecutor exec(rclcpp::ExecutorOptions(), 3);
  exec.add_node(node);
  RCLCPP_INFO(node->get_logger(), "Starting executor...");
  exec.spin();
  return 0;
}