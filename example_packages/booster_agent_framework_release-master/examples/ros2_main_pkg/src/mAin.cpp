#include "example_agent.hpp"
int main(int argc, char *argv[]) {
    rclcpp::init(argc, argv);
    auto node = std::make_shared<MyAgentNode>();
    rclcpp::executors::MultiThreadedExecutor exec(rclcpp::ExecutorOptions(), 3);
    exec.add_node(node);
    RCLCPP_INFO(node->get_logger(), "Starting executor...");
    exec.spin();
    rclcpp::shutdown();
    return 0;
}