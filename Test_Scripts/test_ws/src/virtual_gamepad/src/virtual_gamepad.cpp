#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <unistd.h>

#include <atomic>
#include <mutex>
#include <string>
#include <thread>

#include "rclcpp/rclcpp.hpp"
#include "booster_interface/msg/remote_controller_state.hpp"

#include "rclcpp/rclcpp.hpp"

#include <cmath>
#include <cstring>
#include <stdexcept>

struct RemoteControllerInput{
    uint32_t event;
    float lx;
    float ly;
    float rx;
    float ry;
    bool a;
    bool b;
    bool x;
    bool y;
    bool lb;
    bool rb;
    bool lt;
    bool rt;
    bool ls;
    bool rs;
    bool back;
    bool start;
    bool hat_c;
    bool hat_u;
    bool hat_d;
    bool hat_l;
    bool hat_r;
    bool hat_lu;
    bool hat_ld;
    bool hat_ru;
    bool hat_rd;
    uint8_t hat_pos;
};

class VirtualGamepadNode : public rclcpp::Node 
{
    rclcpp::Publisher<booster_interface::msg::RemoteControllerState>::SharedPtr virtual_gamepad_pub_;
    rclcpp::TimerBase::SharedPtr timer_;

    public:
        VirtualGamepadNode() : Node("virtual_gamepad_node")
        {
            virtual_gamepad_pub_ = this->create_publisher<booster_interface::msg::RemoteControllerState>("remote_controller_state", 10);
            timer_ = create_wall_timer(
                std::chrono::seconds(1),
                std::bind(&VirtualGamepadNode::on_timer, this));
            
        }

        ~VirtualGamepadNode()
        {
        }

        void on_timer()
        {
            booster_interface::msg::RemoteControllerState msg;
            // Fill in the message with the current state of the virtual gamepad
            // RemoteControllerInput input;
            // Here you would read the actual state of the virtual gamepad and fill in the input structure
            // For example, you could set some dummy values for testing
            msg.event = 0; // Example event code
            msg.lx = 0.0f; // Left stick X-axis
            msg.ly = 0.0f; // Left stick Y-axis
            msg.rx = 0.0f; // Right stick X-axis
            msg.ry = 0.0f; // Right stick Y-axis
            msg.a = true; // A button
            msg.b = false; // B button
            msg.x = false; // X button
            msg.y = false; // Y button
            msg.lb = false; // Left bumper
            msg.rb = false; // Right bumper
            msg.lt = false; // Left trigger
            msg.rt = false; // Right trigger
            msg.ls = false; // Left stick button
            msg.rs = false; // Right stick button
            msg.back = false; // Back button
            msg.start = false; // Start button
            msg.hat_c = false; // D-pad center
            msg.hat_u = false; // D-pad up
            msg.hat_d = false; // D-pad down
            msg.hat_l = false; // D-pad left
            msg.hat_r = false; // D-pad right
            msg.hat_lu = false; // D-pad left-up
            msg.hat_ld = false; // D-pad left-down
            msg.hat_ru = false; // D-pad right-up
            msg.hat_rd = false; // D-pad right-down
            msg.hat_pos = 0; // D-pad position
            
            virtual_gamepad_pub_->publish(msg);
        }

};

int main(int argc, char *argv[])
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<VirtualGamepadNode>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}