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
    unint32_t event;
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
}

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
                std::bind(&RobotCommsNode::on_timer, this));
            
        }

        ~VirtualGamepadNode()
        {
        }

        void on_timer()
        {
            booster_interface::msg::RemoteControllerState msg;
            // Fill in the message with the current state of the virtual gamepad
            RemoteControllerInput input;
            // Here you would read the actual state of the virtual gamepad and fill in the input structure
            // For example, you could set some dummy values for testing
            input.event = 0; // Example event code
            input.lx = 1.0f; // Left stick X-axis
            input.ly = 2.0f; // Left stick Y-axis
            input.rx = 3.0f; // Right stick X-axis
            input.ry = 4.0f; // Right stick Y-axis
            input.a = false; // A button
            input.b = false; // B button
            input.x = false; // X button
            input.y = false; // Y button
            input.lb = false; // Left bumper
            input.rb = false; // Right bumper
            input.lt = false; // Left trigger
            input.rt = false; // Right trigger
            input.ls = false; // Left stick button
            input.rs = false; // Right stick button
            input.back = false; // Back button
            input.start = false; // Start button
            input.hat_c = false; // D-pad center
            input.hat_u = false; // D-pad up
            input.hat_d = false; // D-pad down
            input.hat_l = false; // D-pad left
            input.hat_r = false; // D-pad right
            input.hat_lu = false; // D-pad left-up
            input.hat_ld = false; // D-pad left-down
            input.hat_ru = false; // D-pad right-up
            input.hat_rd = false; // D-pad right-down
            input.hat_pos = 0; // D-pad position

            virtual_gamepad_pub_->publish(msg);
        }

}